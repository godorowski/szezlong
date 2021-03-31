from typing import Optional
from datetime import datetime

from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .models import Bed, Hospital
from .forms import BedCreateForm
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from config import available, children_available


def beds_list(request: HttpRequest, hospital_id: str, param: Optional[str] = None) -> HttpResponse:
    template_name = 'beds/list.html'

    hospital = Hospital.objects.get(pk=hospital_id)
    hospitals = []
    beds = hospital.bed_set.all()
    if param is not None:
        if param == "all":
            beds = available(beds)
        elif param == "respirators":
            beds = available(beds).filter(respirator=True)
        elif param == "oxygen":
            beds = available(beds).filter(respirator=False, oxygen=True)
        elif param == "all-children":
            beds = beds.filter(child=True)
        elif param == "children":
            beds = children_available(beds)
        elif param == "respirators-children":
            beds = children_available(beds).filter(respirator=True)
        elif param == "oxygen-children":
            beds = children_available(beds).filter(respirator=False, oxygen=True)
    hospitals.append([hospital, beds])

    context = {
        "hospitals": hospitals,
    }

    return render(
        request,
        template_name,
        context
    )


class BedsList(ListView):
    model = Bed
    template_name = 'beds/list.html'
    context_object_name = 'beds'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class BedsCreate(CreateView):
    model = Bed
    template_name = 'beds/create.html'
    form_class = BedCreateForm
    context_object_name = 'bed'

    def get_success_url(self):
        return reverse_lazy('beds-list', kwargs={
            'hospital_id': self.object.hospital.pk
        })


class BedsUpdate(UpdateView):
    model = Bed
    template_name = 'beds/update.html'
    fields = '__all__'
    context_object_name = 'bed'
    success_url = reverse_lazy('beds-list')


class BedsDelete(DeleteView):
    model = Bed
    template_name = 'beds/delete.html'
    success_url = reverse_lazy('beds-list')
