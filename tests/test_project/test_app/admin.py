from django.contrib import admin

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteListFilter
from django.contrib.admin import ModelAdmin

from .models import RelatedModel, ExampleModel


@admin.register(ExampleModel)
class ExampleModelAdmin(AutocompleteFilterMixin, ModelAdmin):
    search_fields = ("name",)


@admin.register(RelatedModel)
class RelatedModelAdmin(AutocompleteFilterMixin, ModelAdmin):
    list_filter = (("example_model", AutocompleteListFilter),)
