from django.db import models


class GenericModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ExtraDataModelMixin(models.Model):
    extra_data = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True
