from django.db import models


class ExampleModel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class RelatedModel(models.Model):
    example_model = models.ForeignKey(ExampleModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
