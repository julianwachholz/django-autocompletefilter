django-autocompletefilter
=========================

A django application that lets you use the built in autocomplete function of the
django admin to filter in admin list views by foreign key relations, or by any value you can search.

.. image:: https://pbs.twimg.com/media/DgmzYLbW4AA9oL3.jpg:large

Usage
-----

#. Install the package, for example from PyPi::

    pip install django-autocompletefilter

#. Add ``autocompletefilter`` to your ``INSTALLED_APPS`` setting.

#. Create and register a model admin for the model you want to filter by.
   Ensure it has ``search_fields`` specified for autocomplete to work.

#. In your second model admin, use the ``AutocompleteFilterMixin`` on your class and
   add the desired foreign key attribute to filter by to the ``list_filter``
   items by using the AutocompleteListFilter class::

    from autocompletefilter.admin import AutocompleteFilterMixin
    from autocompletefilter.filters import AutocompleteListFilter

    class FooAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
        list_filter = (
            ('bar', AutocompleteListFilter),
        )


Filtering by any value
----------------------

For a value that isn't a foreign key (a text field, a JSON list, a computed lookup), or a
foreign key you'd rather search your own way, subclass AutocompleteFilter: a
SimpleListFilter whose choices are searched as you type instead of listed. Implement
search(request, term), returning (value, label) pairs (a list, or a queryset of
pairs, served in pages of page_size), and queryset() as usual. label(request,
value) names the chosen value (default: the value itself). self.model_admin is there
for search()::

    from autocompletefilter.admin import AutocompleteFilterMixin
    from autocompletefilter.filters import AutocompleteFilter

    class CountryFilter(AutocompleteFilter):
        title = "country"
        parameter_name = "country"

        def search(self, request, term):
            countries = (
                self.model_admin.get_queryset(request)
                .filter(country__icontains=term)
                .order_by("country")
                .values_list("country", flat=True)
                .distinct()
            )
            return [(country, country) for country in countries]

        def queryset(self, request, queryset):
            if self.value():
                return queryset.filter(country=self.value())
            return queryset

    class VisitAdmin(AutocompleteFilterMixin, admin.ModelAdmin):
        list_filter = (CountryFilter,)

AutocompleteFilterMixin serves the searches at <changelist>/autocomplete-filter/<parameter_name>/
(URL name <app_label>_<model_name>_autocomplete_filter), for staff who may view the model,
and only for the filters in the admin's list_filter.

Status of this project
----------------------

This project is currently using a rather hacky way to implement this.
Caution is advised when using it.

Using multiple autocomplete filters on the same page does work.

Tested with Django 4.2 to 6.1.


Contributing
------------

All suggestions are welcome. Especially about ways to make this cleaner.

To run the tests::

    pip install -e ".[test]"
    pytest


Common issues
-------------

- **Reverse for '<app_name>_<model_name>_autocomplete' not found.**

  You must register a model admin with ``search_fields`` for the model you want to look up.

- **The results could not be loaded.**

  You likely forgot to specify ``search_fields`` on your model admin for the model you want to look up.
