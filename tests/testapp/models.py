from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(
        Author, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title
