from typing import TypeVar, Generic, List, Optional, Callable, Type, Any, Tuple, Dict, Sequence, Iterable, Iterator
import logging
from django.db import models, transaction
from django.db.models import F, QuerySet, Q
from django.utils import timezone

from cqrsex.Application.Interfaces.Common.IGenericRepository import IGenericRepository


logger = logging.getLogger(__name__)

T = TypeVar('T', bound=models.Model)


class GenericRepository(IGenericRepository[T], Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        # cached model capabilities
        self._has_vendor: bool = any(getattr(f, "attname", "") == "vendor_id" for f in self.model._meta.fields)
        self._has_active: bool = any(getattr(f, "attname", "") == "is_active" for f in self.model._meta.fields)
        self._has_deleted: bool = any(getattr(f, "attname", "") == "is_deleted" for f in self.model._meta.fields)

    # ---------------------------
    # Helpers
    # ---------------------------
    def _supports_vendor(self) -> bool:
        return self._has_vendor

    def _supports_active(self) -> bool:
        return self._has_active

    def _maybe_filter_not_deleted(self, qs: QuerySet) -> QuerySet:
        return qs.filter(is_deleted=False) if self._has_deleted else qs

    @staticmethod
    def _truthy(v) -> bool:
        if v is None:
            return False
        s = str(v).strip().lower()
        return s in {"1", "true", "yes", "on", "y", "t"}

    # ---------------------------
    # Base helpers (legacy "safe" mode)
    # ---------------------------
    def _base_queryset(self) -> QuerySet:
        qs = self.model.objects.all()
        if self._has_deleted:
            qs = qs.filter(is_deleted=False)
        return qs

    def _apply_soft_delete_filter(self, filters: dict) -> dict:
        # keep existing behavior for find*/get* (SAFE mode)
        if self._has_deleted:
            filters = dict(filters)  # don't mutate caller's dict
            filters["is_deleted"] = False
        return filters

    # ---------------------------
    # Gets / Lists (SAFE mode)
    # ---------------------------
    def get_by_id(self, id: Any) -> Optional[T]:
        return self._base_queryset().filter(id=id).first()

    def get_by_id_for_update(self, id: Any) -> Optional[T]:
        qs = self.model.objects.select_for_update()
        if self._has_deleted:
            qs = qs.filter(is_deleted=False)
        return qs.filter(id=id).first()

    def get_by_ids_for_update(self, ids: List[Any]) -> List[T]:
        qs = self.model.objects.select_for_update()
        if self._has_deleted:
            qs = qs.filter(is_deleted=False)
        return list(qs.filter(id__in=ids))

    def get_all(self) -> List[T]:
        return list(self._base_queryset())

    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        *,
        vendor_id: Optional[Any] = None,
        order_by: Optional[Iterable[str]] = None,
        **filters,
    ) -> Tuple[List[T], int]:
        page = max(int(page or 1), 1)
        page_size = max(int(page_size or 10), 1)

        queryset = self._base_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        if vendor_id is not None and self._supports_vendor():
            queryset = queryset.filter(vendor_id=vendor_id)
        if order_by:
            queryset = queryset.order_by(*order_by)

        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        return list(queryset[start:end]), total_count

    def get_all_as(self, selector: Callable[[T], Any]) -> List[Any]:
        return [selector(item) for item in self._base_queryset()]

    # ---------------------------
    # Mutations
    # ---------------------------
    def add(self, entity: T, vendor_context: Optional[Any] = None) -> T:
        if vendor_context and self._supports_vendor() and getattr(entity, "vendor_id", None) is None:
            setattr(entity, "vendor_id", getattr(vendor_context, "id", None))
        entity.save()
        return entity

    def update(self, entity: T) -> T:
        logger.debug(f"Updating entity id {getattr(entity, 'id', None)}")
        entity.save()
        return entity

    def remove(self, entity: T) -> None:
        # soft delete if supported, else hard delete
        if self._has_deleted:
            setattr(entity, "is_deleted", True)
            if hasattr(entity, "deleted_at"):
                setattr(entity, "deleted_at", timezone.now())
            entity.save(update_fields=["is_deleted"] + (["deleted_at"] if hasattr(entity, "deleted_at") else []))
        else:
            entity.delete()

    def delete_permanently(self, entity: T) -> None:
        entity.delete()

    def get_soft_data(self, entity: T) -> T:
        # legacy alias to soft delete
        if self._has_deleted:
            entity.is_deleted = True
            if hasattr(entity, "deleted_at"):
                entity.deleted_at = timezone.now()
            entity.save(update_fields=["is_deleted"] + (["deleted_at"] if hasattr(entity, "deleted_at") else []))
        return entity

    # ---------------------------
    # Finds (SAFE mode – inject is_deleted=False if present)
    # ---------------------------
    def find(self, **filters) -> List[T]:
        filters = self._apply_soft_delete_filter(filters)
        return list(self.model.objects.filter(**filters))

    def find_one(self, **filters) -> Optional[T]:
        filters = self._apply_soft_delete_filter(filters)
        return self.model.objects.filter(**filters).first()

    def find_one_for_update(self, **filters) -> Optional[T]:
        filters = self._apply_soft_delete_filter(filters)
        return self.model.objects.select_for_update().filter(**filters).first()

    def find_custom(self, filter_func: Callable[[QuerySet], QuerySet]) -> List[T]:
        return list(filter_func(self._base_queryset()))

    def atomic_increment(self, id: Any, field: str, amount: int = 1) -> bool:
        qs = self.model.objects
        if self._has_deleted:
            qs = qs.filter(is_deleted=False)
        return qs.filter(id=id).update(**{field: F(field) + amount}) > 0

    def bulk_add(self, entities: List[T], vendor_context: Optional[Any] = None) -> None:
        if vendor_context and self._supports_vendor():
            for entity in entities:
                if getattr(entity, "vendor_id", None) is None:
                    setattr(entity, "vendor_id", getattr(vendor_context, "id", None))
        self.model.objects.bulk_create(entities)

    def bulk_update(self, entities: List[T], fields: List[str]) -> None:
        self.model.objects.bulk_update(entities, fields)

    # ============================================================
    # PROJECTIONS (RAW mode – NO soft-delete injection)
    # ============================================================
    def get_by_id_values(
        self,
        id: Any,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        qs = self.model.objects.filter(id=id)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        return qs.values(*fields).first()

    def get_all_values(
        self,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        qs = self.model.objects.all()
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        return list(qs.values(*fields))

    def find_values(
        self,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> List[Dict[str, Any]]:
        qs = self.model.objects.filter(**filters)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        return list(qs.values(*fields))

    def find_one_values(
        self,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> Optional[Dict[str, Any]]:
        qs = self.model.objects.filter(**filters)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        return qs.values(*fields).first()

    def find_values_list(
        self,
        field: str,
        *,
        distinct: bool = False,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> List[Any]:
        qs = self.model.objects.filter(**filters)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        qs = qs.values_list(field, flat=True)
        if distinct:
            qs = qs.distinct()
        return list(qs)

    def select(
        self,
        fields: Sequence[str],
        *,
        as_list: bool = False,
        distinct: bool = False,
        order_by: Optional[Iterable[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> List[Any]:
        qs = self.model.objects.filter(**filters)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        if order_by:
            qs = qs.order_by(*order_by)

        if as_list:
            if len(fields) == 1:
                qs = qs.values_list(fields[0], flat=True)
            else:
                qs = qs.values_list(*fields)
        else:
            qs = qs.values(*fields)

        if distinct:
            qs = qs.distinct()
        if offset:
            qs = qs[offset:]
        if limit is not None:
            qs = qs[:limit]
        return list(qs)

    def iter_values(
        self,
        fields: Sequence[str],
        *,
        chunk_size: int = 2000,
        order_by: Optional[Iterable[str]] = None,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> Iterator[Dict[str, Any]]:
        qs = self.model.objects.filter(**filters)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)
        if order_by:
            qs = qs.order_by(*order_by)

        for row in qs.values(*fields).iterator(chunk_size=chunk_size):
            yield row

    # ---------------------------
    # Projections: paginated
    # ---------------------------
    def paginate_values(
        self,
        fields: Sequence[str],
        *,
        page: int = 1,
        page_size: int = 20,
        order_by: Optional[Iterable[str]] = None,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> Tuple[List[Dict[str, Any]], int]:
      
        page = max(int(page or 1), 1)
        page_size = max(int(page_size or 20), 1)

        include_deleted = self._truthy(filters.pop("with_deleted", None))
        include_global = self._truthy(filters.pop("include_global", None))
        search = str(filters.pop("q", "") or "").strip()

        qs = self.model.objects.all()
        if self._has_deleted and not include_deleted:
            qs = qs.filter(is_deleted=False)

        if vendor_id is not None and self._supports_vendor():
            if include_global:
                qs = qs.filter(Q(vendor_id=vendor_id) | Q(vendor_id__isnull=True))
            else:
                qs = qs.filter(vendor_id=vendor_id)

        if search:
            qs = qs.filter(
                Q(en_name__icontains=search) |
                Q(ar_name__icontains=search) |
                Q(description__icontains=search)
            )

        if filters:
            qs = qs.filter(**filters)

        total = qs.count()

        if order_by:
            qs = qs.order_by(*order_by)

        start = (page - 1) * page_size
        end = start + page_size
        rows = list(qs.values(*fields)[start:end])
        return rows, total

    # ---------------------------
    # Active helpers
    # ---------------------------
    def set_active_by_id(
        self,
        id: Any,
        is_active: bool,
        *,
        vendor_id: Optional[Any] = None,
        modified_by: Optional[str] = None,
    ) -> bool:
        if not self._supports_active():
            raise AttributeError(f"{self.model.__name__} has no 'is_active' field")

        qs = self.model.objects
        qs = self._maybe_filter_not_deleted(qs)

        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)

        now = timezone.now()
        update_data: Dict[str, Any] = {"is_active": is_active}

        attnames = {getattr(f, "attname", "") for f in self.model._meta.fields}
        if "updated_at" in attnames:
            update_data["updated_at"] = now
        if "modified_at" in attnames:
            update_data["modified_at"] = now
        if modified_by and "modified_by" in attnames:
            update_data["modified_by"] = modified_by

        return qs.filter(id=id).update(**update_data) > 0

    def activate_by_id(self, id: Any, *, vendor_id: Optional[Any] = None, modified_by: Optional[str] = None) -> bool:
        return self.set_active_by_id(id, True, vendor_id=vendor_id, modified_by=modified_by)

    def deactivate_by_id(self, id: Any, *, vendor_id: Optional[Any] = None, modified_by: Optional[str] = None) -> bool:
        return self.set_active_by_id(id, False, vendor_id=vendor_id, modified_by=modified_by)

    def toggle_active_by_id(self, id: Any, *, vendor_id: Optional[Any] = None, modified_by: Optional[str] = None) -> Optional[bool]:
        if not self._supports_active():
            raise AttributeError(f"{self.model.__name__} has no 'is_active' field")

        with transaction.atomic():
            row = self.get_by_id_for_update(id)
            if not row:
                return None
            if vendor_id is not None and self._supports_vendor():
                if str(getattr(row, "vendor_id", None)) != str(vendor_id):
                    return None

            if self._has_deleted and bool(getattr(row, "is_deleted", False)):
                return None

            new_val = not bool(getattr(row, "is_active", False))
            setattr(row, "is_active", new_val)

            update_fields = ["is_active"]
            now = timezone.now()

            if hasattr(row, "updated_at"):
                setattr(row, "updated_at", now)
                update_fields.append("updated_at")
            if hasattr(row, "modified_at"):
                setattr(row, "modified_at", now)
                update_fields.append("modified_at")
            if modified_by and hasattr(row, "modified_by"):
                setattr(row, "modified_by", modified_by)
                update_fields.append("modified_by")

            row.save(update_fields=update_fields)
            return new_val

    def set_active(self, entity: T, is_active: bool) -> T:
        if not self._supports_active():
            raise AttributeError(f"{self.model.__name__} has no 'is_active' field")
        setattr(entity, "is_active", is_active)
        update_fields = ["is_active"]
        now = timezone.now()
        if hasattr(entity, "updated_at"):
            setattr(entity, "updated_at", now)
            update_fields.append("updated_at")
        if hasattr(entity, "modified_at"):
            setattr(entity, "modified_at", now)
            update_fields.append("modified_at")
        entity.save(update_fields=update_fields)
        return entity

    def bulk_set_active(
        self,
        ids: List[Any],
        is_active: bool,
        *,
        vendor_id: Optional[Any] = None,
        modified_by: Optional[str] = None,
    ) -> int:
        if not self._supports_active():
            raise AttributeError(f"{self.model.__name__} has no 'is_active' field")

        if not ids:
            return 0

        qs = self.model.objects.filter(id__in=ids)
        qs = self._maybe_filter_not_deleted(qs)
        if vendor_id is not None and self._supports_vendor():
            qs = qs.filter(vendor_id=vendor_id)

        now = timezone.now()
        update_data: Dict[str, Any] = {"is_active": is_active}

        attnames = {getattr(f, "attname", "") for f in self.model._meta.fields}
        if "updated_at" in attnames:
            update_data["updated_at"] = now
        if "modified_at" in attnames:
            update_data["modified_at"] = now
        if modified_by and "modified_by" in attnames:
            update_data["modified_by"] = modified_by

        return qs.update(**update_data)

    def bulk_activate(self, ids: List[Any], *, vendor_id: Optional[Any] = None, modified_by: Optional[str] = None) -> int:
        return self.bulk_set_active(ids, True, vendor_id=vendor_id, modified_by=modified_by)

    def bulk_deactivate(self, ids: List[Any], *, vendor_id: Optional[Any] = None, modified_by: Optional[str] = None) -> int:
        return self.bulk_set_active(ids, False, vendor_id=vendor_id, modified_by=modified_by)
