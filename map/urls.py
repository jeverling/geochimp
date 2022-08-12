"""map app URL Configuration."""
from django.urls import path

from .views import create_map

urlpatterns = [
    path(
        "",
        create_map,
        name="create_map",
    ),
]
