# blog/api/viewsets.py
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from cqrsex.Bootstrap.container import get_mediator

from cqrsex.Application.CQRS.BlogPosts.Queries.List.Request import ListBlogPosts
from cqrsex.Application.CQRS.BlogPosts.Queries.Get.Request import GetBlogPost
from cqrsex.Application.CQRS.BlogPosts.Commands.Create.Request import CreateBlogPost
from cqrsex.Application.CQRS.BlogPosts.Commands.Update.Request import UpdateBlogPost
from cqrsex.Application.CQRS.BlogPosts.Commands.Delete.Request import DeleteBlogPost

class BlogPostViewSet(ViewSet):
    def list(self, request):
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        author_id = request.query_params.get("author_id")
        author_id = int(author_id) if author_id is not None else None
        res = get_mediator().send(ListBlogPosts(page=page, page_size=page_size, author_id=author_id))
        return Response(res.to_dict(), status=res.status.status_code)

    def retrieve(self, request, pk=None):
        res = get_mediator().send(GetBlogPost(id=int(pk)))
        return Response(res.to_dict(), status=res.status.status_code)

    def create(self, request):
        p = request.data or {}
        res = get_mediator().send(CreateBlogPost(
            title=p.get("title", ""),
            body=p.get("body", ""),
            author_id=int(p.get("author_id", 0)),
        ))
        return Response(res.to_dict(), status=res.status.status_code)

    def update(self, request, pk=None):
        p = request.data or {}
        res = get_mediator().send(UpdateBlogPost(
            id=int(pk),
            title=p.get("title"),
            body=p.get("body"),
        ))
        return Response(res.to_dict(), status=res.status.status_code)

    def destroy(self, request, pk=None):
        res = get_mediator().send(DeleteBlogPost(id=int(pk)))
        return Response(res.to_dict(), status=res.status.status_code)
