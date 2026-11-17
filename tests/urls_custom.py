"""Only the custom-named admin site: there is no "admin" namespace to reverse."""
from django.urls import path

from .testapp.admin import custom_site

urlpatterns = [
    path("custom/", custom_site.urls),
]
