django-autocompletefilter
=========================

A django application that lets you use the built in autocomplete function of the
django admin to filter in admin list views by foreign key relations.

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


Status of this project
----------------------

This project is currently using a rather hacky way to implement this.
Caution is advised when using it.

Using multiple autocomplete filters on the same page does work.

Currently only tested on Python 3.6


Contributing
------------

All suggestions are welcome. Especially about ways to make this cleaner.


Common issues
-------------

- **Reverse for '<app_name>_<model_name>_autocomplete' not found.**

  You must register a model admin with ``search_fields`` for the model you want to look up.

- **The results could not be loaded.**

  You likely forgot to specify ``search_fields`` on your model admin for the model you want to look up.
