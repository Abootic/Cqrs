from injector import Module, provider, singleton, Injector
from typing import Callable, Dict, Type, Any
from cqrsex.Application.Mediator.mediator import Mediator
from cqrsex.Application.Mediator.pipeline import TransactionBehavior
from cqrsex.Application.Interfaces.Common.IUnitOfWork import IUnitOfWork

# Requests/Handlers
from cqrsex.Application.CQRS.BlogPosts.Commands.Create.Request import CreateBlogPost
from cqrsex.Application.CQRS.BlogPosts.Commands.Create.Handler import CreateBlogPostHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Update.Request import UpdateBlogPost
from cqrsex.Application.CQRS.BlogPosts.Commands.Update.Handler import UpdateBlogPostHandler
from cqrsex.Application.CQRS.BlogPosts.Commands.Delete.Request import DeleteBlogPost
from cqrsex.Application.CQRS.BlogPosts.Commands.Delete.Handler import DeleteBlogPostHandler
from cqrsex.Application.CQRS.BlogPosts.Queries.Get.Request import GetBlogPost
from cqrsex.Application.CQRS.BlogPosts.Queries.Get.Handler import GetBlogPostHandler
from cqrsex.Application.CQRS.BlogPosts.Queries.List.Request import ListBlogPosts
from cqrsex.Application.CQRS.BlogPosts.Queries.List.Handler import ListBlogPostsHandler

class MediatorModule(Module):
    @singleton
    @provider
    def provide_mediator(
        self,
        injector: Injector,
        uow_factory: Callable[[], IUnitOfWork],
    ) -> Mediator:
        # use factories (lazy build)
        handlers: Dict[Type[Any], Callable[[], Any]] = {
            CreateBlogPost:  lambda i=injector: i.get(CreateBlogPostHandler),
            UpdateBlogPost:  lambda i=injector: i.get(UpdateBlogPostHandler),
            DeleteBlogPost:  lambda i=injector: i.get(DeleteBlogPostHandler),
            GetBlogPost:     lambda i=injector: i.get(GetBlogPostHandler),
            ListBlogPosts:   lambda i=injector: i.get(ListBlogPostsHandler),
        }
        behaviors = [TransactionBehavior(uow_factory)]
        return Mediator(handlers=handlers, behaviors=behaviors)
