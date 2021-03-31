import datetime
from email.utils import format_datetime

from django.utils.cache import get_conditional_response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import MethodNotAllowed


def get_datetime(last_modified_date):
    return datetime.datetime.strptime(last_modified_date, '%a, %d %b %Y %H:%M:%S %Z')


def get_last_modified_date(dt):
    return format_datetime(dt)


class GenericModelViewSet(ModelViewSet):

    def list(self, request, *args, **kwargs):
        """

        """
        response = super().list(request, *args, **kwargs)
        return response

    def create(self, request, *args, **kwargs):
        """

        """
        response = super().create(request, *args, **kwargs)
        return response

    def retrieve(self, request, *args, **kwargs):
        """

        """
        response = super().retrieve(request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        """

        """
        response = super().update(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        """

        """
        response = super().destroy(request, *args, **kwargs)
        return response


class ConditionalResponseViewSet(ModelViewSet):

    last_modified_field = 'last_modified_on'
    create_field = 'created_on'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        instance = self.get_object()
        last_modified = getattr(instance, "last_modified_on", None)
        if last_modified is not None:
            response["Last-Modified"] = get_last_modified_date(last_modified)
        return response

    def condition_response(self, request):
        instance = self.get_object()
        last_modified = getattr(instance, "last_modified_on", None)
        return get_conditional_response(
            request,
            etag=None,
            last_modified=last_modified,
        )

    def update(self, request, *args, **kwargs):
        response = self.condition_response(request=request)
        if response is None:
            response = super().update(request, *args, **kwargs)
        return response

    def destroy(self, request, *args, **kwargs):
        response = self.condition_response(request=request)
        if response is None:
            response = super().destroy(request, *args, **kwargs)
        return response

    def partial_update(self, request, *args, **kwargs):
        response = self.condition_response(request=request)
        if response is None:
            response = super().partial_update(request, *args, **kwargs)
        return response
