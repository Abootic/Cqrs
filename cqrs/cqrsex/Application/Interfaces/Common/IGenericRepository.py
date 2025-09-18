# rasapi/Application/Interfaces/Common/IGenericRepository.py

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, List, Optional, Callable, Any, Tuple,
    Dict, Sequence, Iterable, Iterator
)
from django.db import models
from django.db.models import QuerySet

T = TypeVar('T', bound=models.Model)

from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, List, Optional, Callable, Any, Tuple,
    Dict, Sequence, Iterable, Iterator
)
from django.db import models
class IGenericRepository(ABC, Generic[T]):
    # ---------- Base / Safe ----------
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]: ...
    @abstractmethod
    def get_by_id_for_update(self, id: Any) -> Optional[T]: ...
    @abstractmethod
    def get_by_ids_for_update(self, ids: List[Any]) -> List[T]: ...
    @abstractmethod
    def get_all(self) -> List[T]: ...
    @abstractmethod
    def get_paginated(
        self,
        page: int,
        page_size: int,
        *,
        vendor_id: Optional[Any] = None,
        order_by: Optional[Iterable[str]] = None,
        **filters
    ) -> Tuple[List[T], int]: ...
    @abstractmethod
    def get_all_as(self, selector: Callable[[T], Any]) -> List[Any]: ...

    # ---------- Mutations ----------
    @abstractmethod
    def add(self, entity: T, vendor_context: Optional[Any] = None) -> T: ...
    @abstractmethod
    def update(self, entity: T) -> T: ...
    @abstractmethod
    def remove(self, entity: T) -> None: ...
    @abstractmethod
    def delete_permanently(self, entity: T) -> None: ...
    @abstractmethod
    def get_soft_data(self, entity: T) -> T: ...

    # ---------- Finds (safe mode; may inject soft-delete filter) ----------
    @abstractmethod
    def find(self, **filters) -> List[T]: ...
    @abstractmethod
    def find_one(self, **filters) -> Optional[T]: ...
    @abstractmethod
    def find_one_for_update(self, **filters) -> Optional[T]: ...
    

    @abstractmethod
    def find_custom(self, filter_func: Callable[[QuerySet], QuerySet]) -> List[T]: ...
    @abstractmethod
    def atomic_increment(self, id: Any, field: str, amount: int = 1) -> bool: ...
    @abstractmethod
    def bulk_add(self, entities: List[T], vendor_context: Optional[Any] = None) -> None: ...
    @abstractmethod
    def bulk_update(self, entities: List[T], fields: List[str]) -> None: ...


    @abstractmethod
    def get_by_id_values(
        self,
        id: Any,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def get_all_values(
        self,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
    ) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def find_values(
        self,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def find_one_values(
        self,
        fields: Sequence[str],
        *,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> Optional[Dict[str, Any]]: ...

    @abstractmethod
    def find_values_list(
        self,
        field: str,
        *,
        distinct: bool = False,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> List[Any]: ...

    @abstractmethod
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
    ) -> List[Any]: ...

    @abstractmethod
    def iter_values(
        self,
        fields: Sequence[str],
        *,
        chunk_size: int = 2000,
        order_by: Optional[Iterable[str]] = None,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> Iterator[Dict[str, Any]]: ...

    @abstractmethod
    def paginate_values(
        self,
        fields: Sequence[str],
        *,
        page: int = 1,
        page_size: int = 20,
        order_by: Optional[Iterable[str]] = None,
        vendor_id: Optional[Any] = None,
        **filters
    ) -> Tuple[List[Dict[str, Any]], int]: ...

    # ============================================================
    # Active / Inactive helpers
    # ============================================================
    @abstractmethod
    def set_active_by_id(
        self,
        id: Any,
        is_active: bool,
        *,
        vendor_id: Optional[Any] = None,
    ) -> bool: ...

    @abstractmethod
    def activate_by_id(self, id: Any, *, vendor_id: Optional[Any] = None) -> bool: ...

    @abstractmethod
    def deactivate_by_id(self, id: Any, *, vendor_id: Optional[Any] = None) -> bool: ...

    @abstractmethod
    def toggle_active_by_id(self, id: Any, *, vendor_id: Optional[Any] = None) -> Optional[bool]: ...

    @abstractmethod
    def set_active(self, entity: T, is_active: bool) -> T: ...

    @abstractmethod
    def bulk_set_active(
        self,
        ids: List[Any],
        is_active: bool,
        *,
        vendor_id: Optional[Any] = None,
    ) -> int: ...

    @abstractmethod
    def bulk_activate(self, ids: List[Any], *, vendor_id: Optional[Any] = None) -> int: ...

    @abstractmethod
    def bulk_deactivate(self, ids: List[Any], *, vendor_id: Optional[Any] = None) -> int: ...
