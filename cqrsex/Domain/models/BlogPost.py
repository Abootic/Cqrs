from django.db import models
from django.conf import settings
class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author_id = models.IntegerField()   # cross-db link
    tenant_id = models.CharField(max_length=20, default="main")

    class Meta:
        db_table = "blog_posts"
        managed = True
