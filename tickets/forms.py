from django.forms import ModelForm
from django.forms import fields
from django.utils.translation import gettext_lazy as _

from .models import Ticket


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = "__all__"

