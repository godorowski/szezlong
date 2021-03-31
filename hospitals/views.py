from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from beret_utils import pp

from .models import Hospital, Specialisation


class HospitalList(ListView):
    model = Hospital
    template_name = 'hospitals/list.html'
    context_object_name = 'hospitals'

    def get_context_data(self, *, object_list=None, **kwargs):
        spec_id = self.request.GET.get("spec", None)
        context = super().get_context_data(object_list=object_list, **kwargs)
        specs = Specialisation.objects.all()
        param = self.request.GET.get("param", None)

        hospitals = context["hospitals"]

        if param is not None:
            if param == "all":
                hospitals = (hospital for hospital in hospitals if hospital.available_beds > 0)
            elif param == "all-expired":
                hospitals = (hospital for hospital in hospitals if hospital.total_expires > 0)
            elif param == "all-attentions":
                hospitals = (hospital for hospital in hospitals if hospital.total_attentions > 0)
            elif param == "respirators":
                hospitals = (hospital for hospital in hospitals if hospital.available_respirators > 0)
            elif param == "respirators-expired":
                hospitals = (hospital for hospital in hospitals if hospital.expires_respirators > 0)
            elif param == "respirators-attentions":
                hospitals = (hospital for hospital in hospitals if hospital.attentions_respirators > 0)
            elif param == "oxygen":
                hospitals = (hospital for hospital in hospitals if hospital.available_oxygens > 0)
            elif param == "oxygen-expired":
                hospitals = (hospital for hospital in hospitals if hospital.expires_oxygens > 0)
            elif param == "oxygen-attentions":
                hospitals = (hospital for hospital in hospitals if hospital.attentions_oxygens > 0)
            elif param == "all-children":
                hospitals = (hospital for hospital in hospitals if hospital.total_children > 0)
            elif param == "children":
                hospitals = (hospital for hospital in hospitals if hospital.available_children > 0)
            elif param == "respirators-children":
                hospitals = (hospital for hospital in hospitals if hospital.available_children_respirators > 0)
            elif param == "oxygen-children":
                hospitals = (hospital for hospital in hospitals if hospital.available_children_oxygens > 0)

        if spec_id is None:
            current_spec = None
            hospitals = (hospital for hospital in hospitals)
        else:
            current_spec = Specialisation.objects.get(pk=int(spec_id))
            hospitals = (hospital for hospital in context["hospitals"] if current_spec in hospital.specialisations.all())


        hospitals_specs = [
            [
                hospital,
                [spec for spec in hospital.specialisations.all()],
            ] for hospital in hospitals
        ]

        context.update({
            "param_url": "" if param is None else f"&param={param}",
            "param": param,
            "current_spec": current_spec,
            "specs": specs,
            "hospitals": hospitals_specs
        })

        return context


class HospitalCreate(CreateView):
    model = Hospital
    template_name = 'hospitals/create.html'
    fields = '__all__'
    context_object_name = 'hospital'
    success_url = reverse_lazy('hospital-list')


class HospitalUpdate(UpdateView):
    model = Hospital
    template_name = 'hospitals/update.html'
    fields = '__all__'
    context_object_name = 'hospital'
    success_url = reverse_lazy('hospital-list')


class HospitalDelete(DeleteView):
    model = Hospital
    template_name = 'hospitals/delete.html'
    success_url = reverse_lazy('hospital-list')
