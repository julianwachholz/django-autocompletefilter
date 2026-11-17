from django.contrib import admin

from autocompletefilter.admin import AutocompleteFilterMixin
from autocompletefilter.filters import AutocompleteFilter, AutocompleteListFilter

from .models import Author, Book


class GenreFilter(AutocompleteFilter):
    title = "genre"
    parameter_name = "genre"
    page_size = 2

    def search(self, request, term):
        genres = (
            self.model_admin.get_queryset(request)
            .exclude(genre="")
            .filter(genre__icontains=term)
            .order_by("genre")
            .values_list("genre", flat=True)
            .distinct()
        )
        return [(genre, self.label(request, genre)) for genre in genres]

    def label(self, request, value):
        return value.upper()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(genre=self.value())
        return queryset


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ["name"]


class BookAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
    search_fields = ["title"]
    list_filter = [("author", AutocompleteListFilter), GenreFilter]


custom_site = admin.AdminSite(name="custom")

for site in (admin.site, custom_site):
    site.register(Author, AuthorAdmin)
    site.register(Book, BookAdmin)
