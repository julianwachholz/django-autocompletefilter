from html.parser import HTMLParser
from urllib.parse import parse_qs

import pytest

from .testapp.models import Author, Book


class _Selects(HTMLParser):
    """The filter <select> elements of a page: their attributes and their options."""

    def __init__(self):
        super().__init__()
        self.selects = {}
        self._select = self._option = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "select" and "admin-autocomplete-filter" in attrs.get("class", ""):
            self._select = {"attrs": attrs, "options": []}
            self.selects[attrs["data-field-name"]] = self._select
        elif tag == "option" and self._select is not None:
            self._option = {"value": attrs.get("value"), "text": ""}
            self._select["options"].append(self._option)

    def handle_data(self, data):
        if self._option is not None:
            self._option["text"] += data

    def handle_endtag(self, tag):
        if tag == "option":
            self._option = None
        elif tag == "select":
            self._select = None


def filter_selects(response):
    """{field name: {"attrs": {...}, "options": [{"value", "text"}]}} of a changelist."""
    assert response.status_code == 200
    parser = _Selects()
    parser.feed(response.content.decode())
    return parser.selects


def query(query_string):
    """A "?a=1&b=2" query string as a dict of lists."""
    assert query_string.startswith("?")
    return parse_qs(query_string[1:])


@pytest.fixture
def library(db):
    """Two authors, three books in two genres, and one book without either."""
    tolkien = Author.objects.create(name="Tolkien")
    herbert = Author.objects.create(name="Herbert")
    Book.objects.create(title="The Hobbit", genre="fantasy", author=tolkien)
    Book.objects.create(title="The Silmarillion", genre="fantasy", author=tolkien)
    Book.objects.create(title="Dune", genre="scifi", author=herbert)
    Book.objects.create(title="Untitled")
    return {"tolkien": tolkien, "herbert": herbert}


def titles(response):
    return sorted(book.title for book in response.context["cl"].result_list)
