from django.db import models
from django.conf import settings

from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.fields import ModificationDateTimeField

from .middleware import get_request


class CreatedMixin(object):
    created_on = CreationDateTimeField()


class ModifiedMixin(object):
    last_modified_on = ModificationDateTimeField()


class ChroniclerModel(CreatedMixin, ModifiedMixin, models.Model):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_%(class)s',
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='last_modified_%(class)s',
        blank=True,
        null=True,
        editable=False,
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True

    @classmethod
    def get_user(cls):

        user = None
        request = get_request()
        if request:
            user = getattr(request, 'user', None)

        return user

    def save(self, *args, **kwargs):

        user = self.get_user()

        if self.pk is None:
            self.created_by = user
        self.last_modified_by = user

        super().save(*args, **kwargs)


class ChroniclerModelLogging(ChroniclerModel):

    modified_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='modified_%(class)s'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        user = self.get_user()

        super().save(*args, **kwargs)

        if user:
            self.modified_by.add(user)
