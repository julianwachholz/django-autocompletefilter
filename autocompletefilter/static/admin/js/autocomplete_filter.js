(function($) {
    'use strict';

    $.fn.djangoAdminAutocompleteFilter = function(options) {
        $.each(this, function(i, element) {
            var template = element.dataset.querystring;
            var placeholder = element.dataset.querystringPlaceholder;
            $(element).on('change', function(event) {
                var url;
                if (event.target.value) {
                    url = template.replace(placeholder, event.target.value);
                } else {
                    url = element.dataset.querystringAll;
                }
                window.location = url;
            });
        });
    };

    $(function() {
        $('.admin-autocomplete-filter').djangoAdminAutocompleteFilter();
    });
}(django.jQuery));
