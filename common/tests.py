import json
from test.support import EnvironmentVarGuard

from django.test import RequestFactory
from rest_framework.reverse import reverse
from django.test import TestCase


METHODS = {
    'retrieve':'get',
    'list': 'get',
    'update': 'put',
    'partial_update': 'patch',
    'destroy': 'delete',
    'create': 'post',
}


class RestApiRequestFactory(RequestFactory):

    def __init__(self, basename, **defaults):
        super().__init__(**defaults)
        self.basename = basename

    def get_path(self, path, pk, **kwargs):
        if path is None:
            if pk is None:
                path = "list"
            else:
                path = "detail"
        if pk is not None:
            kwargs["pk"] = pk
        return reverse(f"{self.basename}-{path}", kwargs=kwargs)

    def get(self, path=None, data=None, pk=None, kwargs=None, **extra):
        if data is None:
            data = {}
        if kwargs is None:
            kwargs = {}
        return super().get(self.get_path(path=path, pk=pk, **kwargs), data, **extra)

    def post(self, path=None, data=None, pk=None, kwargs=None, **extra):
        if data is None:
            data = {}
        if kwargs is None:
            kwargs = {}
        return super().post(self.get_path(path=path, pk=pk, **kwargs), data, **extra)

    def patch(self, path=None, data=None, pk=None, kwargs=None, **extra):
        if data is None:
            data = {}
        if kwargs is None:
            kwargs = {}
        return super().patch(self.get_path(path=path, pk=pk, **kwargs), data, **extra)

    def put(self, path=None, data=None, pk=None, kwargs=None, **extra):
        if data is None:
            data = {}
        if kwargs is None:
            kwargs = {}
        return super().put(self.get_path(path=path, pk=pk, **kwargs), data, **extra)

    def delete(self, path=None, pk=None, kwargs=None, data='', content_type='application/octet-stream',
               **extra):
        if kwargs is None:
            kwargs = {}
        return super().delete(self.get_path(path=path, pk=pk, **kwargs), data, **extra)


class RestApiTestCase(TestCase):
    basename = None
    viewset = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def request_factory(self):
        return RestApiRequestFactory(basename=self.basename)

    def action_test(self,
                    action="list",
                    pk=None,
                    data=None,
                    kwargs=None,
                    path=None,
                    method=None,
                    factory_data=None,
                    **extra):

        if kwargs is None:
            kwargs = {}

        if data is not None:
            factory_data = json.dumps(data)
            extra["content_type"] = 'application/json'

        if method is None:
            method = METHODS[action]

        if method == "get":
            if data is not None:
                factory_data = data.items()

        if path is None:
            path = action

        factory = self.request_factory()
        request = getattr(factory, method)(pk=pk, data=factory_data, path=path, kwargs=kwargs, **extra)
        view = self.viewset.as_view({method: action})
        response = view(request, pk=pk)
        return response
