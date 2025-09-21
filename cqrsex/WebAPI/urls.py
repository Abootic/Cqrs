from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cqrsex.WebAPI.Controller.BlogPostController import BlogPostViewSet
router = DefaultRouter()
router.register(r'blog', BlogPostViewSet, basename='blog')
urlpatterns = [
    path('', include(router.urls)),  # Include router URLs (don't add 'api/' here)
]
