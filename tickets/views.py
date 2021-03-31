from typing import Optional

from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView

from .forms import TicketForm
from .models import Bed
from .models import Hospital
from .models import Ticket


from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from config import attentions, expires


def hospitals_list(request: HttpRequest) -> HttpResponse:
    template_name = 'tickets/hospitals_list.html'
    context = {
        "hospitals": Hospital.objects.all(),
    }

    return render(
        request,
        template_name,
        context
    )


class TicketsList(ListView):
    model = Ticket
    template_name = 'tickets/list.html'
    context_object_name = 'tickets'
    mode = None
    hospital = None

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        hospital_id = self.kwargs.get("hospital_id")
        self.mode = self.kwargs.get("mode", "orphans")
        self.hospital = Hospital.objects.get(pk=hospital_id)
        queryset = queryset.filter(hospital_id=hospital_id)
        if self.mode == "orphans":
            queryset = queryset.filter(bed=None)
        elif self.mode == "expires":
            queryset = expires(queryset)
        elif self.mode == "attentions":
            queryset = attentions(queryset)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["hospital"] = self.hospital
        context["mode"] = self.mode
        return context


class TicketsCreate(CreateView):
    model = Ticket
    template_name = 'tickets/create.html'
    form_class = TicketForm
    fields = '__all__'
    context_object_name = 'Ticket'
    beds = None

    def get_success_url(self):
        return reverse_lazy('ticket-list', kwargs={
            'hospital_id': self.object.hospital.pk,
            'mode': "orphans"
        })

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.form_class

        kwargs = self.get_form_kwargs() or {}
        initial = kwargs.get("initial", {})

        bed_id = self.kwargs.get("bed_id")
        if bed_id:
            self.bed = Bed.objects.get(pk=bed_id)
            initial['bed'] = self.bed
            self.hospital = self.bed.hospital
            self.beds = Bed.objects.filter(pk=bed_id)
        else:
            initial["bed"] = None
            hospital_id = self.kwargs.get("hospital_id")
            self.hospital = Hospital.objects.get(pk=hospital_id)
            self.action = self.kwargs.get("action")
            self.beds = Bed.objects.filter(hospital=self.hospital)

        initial['hospital'] = self.hospital
        param = self.action

        if param is not None:
            if param == "all":
                initial.update({
                    "respirator": False,
                    "oxygen":     False
                })
                self.beds = self.beds.filter(ticket__isnull=True, child=False, respirator=False, oxygen=False)
            elif param == "respirators":
                initial.update({
                    "respirator": True,
                    "oxygen":     True
                })
                self.beds = self.beds.filter(ticket__isnull=True, child=False)
                if self.hospital.respirators <= self.hospital.ticket_set.filter(use_respirator=True).count():
                    self.beds = self.beds.filter(respirator=True)
            elif param == "oxygen":
                initial.update({
                    "respirator": False,
                    "oxygen":     True
                })
                self.beds = self.beds.filter(ticket__isnull=True, child=False)
                if self.hospital.oxygens <= self.hospital.ticket_set.filter(use_oxygen=True).count():
                    self.beds = self.beds.filter(respirator=False, oxygen=True)
            elif param == "children":
                initial.update({
                    "respirator": False,
                    "oxygen":     False,
                    "child":      True
                })
                self.beds = self.beds.filter(ticket__isnull=True, child=True, respirator=False, oxygen=False)
            elif param == "respirators-children":
                initial.update({
                    "respirator": False,
                    "oxygen":     False,
                    "child":      True
                })
                self.beds = self.beds.filter(ticket__isnull=True, child=True)
                if self.hospital.respirators <= self.hospital.ticket_set.filter(use_respirator=True).count():
                    self.beds = self.beds.filter(respirator=True)
            elif param == "oxygen-children":
                initial.update({
                    "respirator": False,
                    "oxygen":     False,
                    "child":      True
                })
                self.beds = self.beds.filter(ticket__isnull=True, child=True)
                if self.hospital.oxygens <= self.hospital.ticket_set.filter(use_oxygen=True).count():
                    self.beds = self.beds.filter(respirator=False, oxygen=True)

        kwargs["initial"] = initial
        form = form_class(**kwargs)

        if self.beds.count() > 0:
            form.fields["bed"].queryset = self.beds
        else:
            form.fields["bed"].widget.attrs["readonly"] = True

        form.fields["hospital"].widget.attrs["readonly"] = True

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_beds"] = self.beds.count() > 0
        return context


class TicketsUpdate(UpdateView):
    model = Ticket
    template_name = 'tickets/update.html'
    form_class = TicketForm
    fields = '__all__'
    context_object_name = 'Ticket'
    beds = None

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.form_class

        kwargs = self.get_form_kwargs()

        obj = self.get_object()

        self.beds = obj.hospital.bed_set

        self.beds = self.beds.filter(ticket__isnull=True, respirator=False, oxygen=False)

        if obj.respirator:
            if obj.hospital.respirators <= obj.hospital.ticket_set.filter(use_respirator=True).count():
                self.beds = self.beds.filter(respirator=True)
        elif not obj.respirator and obj.oxygen:
            if obj.hospital.oxygens <= obj.hospital.ticket_set.filter(use_oxygen=True).count():
                self.beds = self.beds.filter(respirator=False, oxygen=True)

        if obj.child:
            self.beds = self.beds.filter(child=True)
        else:
            self.beds = self.beds.filter(child=False)

        form = form_class(**kwargs)

        if self.beds.count() > 0:
            form.fields["bed"].queryset = self.beds
        else:
            form.fields["bed"].widget.attrs["readonly"] = True

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_beds"] = self.beds.count() > 0
        return context

    def get_success_url(self):
        return reverse_lazy('ticket-list', kwargs={
            'hospital_id': self.object.hospital.pk,
            'mode':        "orphans"
        })


class TicketsDelete(DeleteView):
    model = Ticket
    template_name = 'tickets/delete.html'

    def get_success_url(self):
        return reverse_lazy('ticket-list', kwargs={
            'hospital_id': self.object.hospital.pk,
            'mode':        "orphans"
        })
