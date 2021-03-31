from django.forms import ModelForm
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from .models import Bed


class BedCreateForm(ModelForm):
    class Meta:
        model = Bed
        fields = ["hospital", "respirator", "oxygen", "child", "specialisation", "count"]
    count = fields.IntegerField(label=_("Ile łóżek chcesz wygenerować"), initial=1)

    def save(self, commit=True):
        count = self.cleaned_data["count"]
        obj = super().save(commit=False)
        if commit:
            for _ in range(count):
                obj.save()
                obj.code = None
        return obj

