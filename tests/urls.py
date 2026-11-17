from django.contrib import admin
from django.urls import path

from .testapp.admin import custom_site

urlpatterns = [
    path("admin/", admin.site.urls),
    path("custom/", custom_site.urls),
]
