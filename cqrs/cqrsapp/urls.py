


from django.urls import path, include

urlpatterns = [
    path('api/', include('cqrsex.WebAPI.urls')),  # your app-level routes file
]

