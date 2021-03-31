from datetime import timedelta, datetime

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Q

from django_extensions.db.fields import CreationDateTimeField
from django_extensions.db.fields import ModificationDateTimeField
from beret_utils.random_code import Codes
from common import ChroniclerModel

from hospitals.models import Hospital, Specialisation
from beds.models import Bed


def default_expiration_date():
    return datetime.now() + timedelta(hours=6)


class Ticket(models.Model):
    class Meta:
        ordering = ["number"]
    
    FIELDS = [
        "code",
        "description",
        "hospital",
        "bed",
        "respirator",
        "oxygen",
        "child",
        "use_respirator",
        "use_oxygen",
        "expiration_date",
        "canceled",
        "canceled_reason",
        "created_on",
        "last_modified_on",
        "prev"
    ]

    code = models.CharField(_("Kod Biletu"), max_length=16, primary_key=True, blank=True)
    number = models.CharField(_("Numer Pacjenta"), max_length=128, db_index=True, blank=True)
    hospital = models.ForeignKey(Hospital, verbose_name=_("Szpital"), on_delete=models.CASCADE)
    bed = models.OneToOneField(Bed, verbose_name=_("Łóżko"), on_delete=models.SET_NULL, null=True, blank=True)
    respirator = models.BooleanField(_("Potrzebny Respirator"), default=False)
    oxygen = models.BooleanField(_("Potrzebny Tlen"), default=False)
    child = models.BooleanField(_("Potrzebne Łóżko Dziecięce"), default=False)
    use_respirator = models.BooleanField(_("Użyty Mobilny Respirator"), default=False)
    use_oxygen = models.BooleanField(_("Użyty Mobilny Tlen"), default=False)
    expiration_date = models.DateTimeField(
        _("Data Ważności"),
        null=True,
        blank=True,
        editable=False,
        default=default_expiration_date
    )
    canceled = models.BooleanField(_("Anulowane"), default=False, editable=False)
    canceled_reason = models.TextField(_("Przyczyna Anulowania"), null=True, blank=True, editable=False)
    created_on = CreationDateTimeField()
    last_modified_on = ModificationDateTimeField()
    prev = models.ForeignKey("DeletedTicket", null=True, editable=False, on_delete=models.CASCADE)

    @property
    def to_dict(self) -> dict:
        ticket_dict = {}
        for field in self.FIELDS:
            ticket_dict[field] = getattr(self, field, None)
        return ticket_dict

    def __str__(self):
        return f"{self.code} expire {self.expiration_date.strftime('%d %h %Y %H:%M')}"

    def gen_code(self):
        code_generator = Codes(
            chars=Codes.DEFAULT_CHARS.upper(),
            count=Ticket.objects.count() + DeletedTicket.objects.count() + 1
        )
        while True:
            code = f"{self.hospital.code}:{code_generator()}"
            if not Ticket.objects.filter(code=code).count() and not DeletedTicket.objects.filter(code=code).count():
                return code

    @property
    def is_expired(self):
        return self.expiration_date <= datetime.now()

    @classmethod
    def expires(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects
        return queryset.filter(expiration_date__lte=datetime.now())

    @classmethod
    def attentions(cls, queryset=None):
        queryset = cls.expires(queryset)\
            .filter(Q(oxygen=True) & Q(use_oxygen=False) & Q(bed__oxygen=False))\
            .filter(Q(respirator=True) & Q(use_respirator=False) & Q(bed__respirator=False))\
            .filter(Q(oxygen=False) & Q(use_oxygen=True) | Q(bed__oxygen=True))\
            .filter(Q(respirator=True) & Q(use_respirator=False) & Q(bed__respirator=False))
        return queryset

    @property
    def attention(self):
        reasons = {
            _("Przeterminowany"): self.is_expired,
            _("Brak Łóżka"): self.bed is None
        }
        if self.bed:
            reasons.update({
                _("Nie Ma Tlenu"): self.oxygen and not (self.use_oxygen or self.bed.oxygen),
                _("Nie Ma Respiratora"): self.respirator and not (self.use_respirator or self.bed.respirator),
                _("Blokuje Tlen"): not self.oxygen and (self.use_oxygen or self.bed.oxygen),
                _("Blokuje Respirator"): not self.respirator and (self.use_respirator or self.bed.respirator),
            })

        # if not any(reasons.values()):
        #     return None
        return [text for text, show in reasons.items() if show]

    def save(self, *args, **kwargs):
        if self.code:
            self.archive()
            self.prev_id = self.code

        self.code = self.gen_code()
        return super().save(*args, **kwargs)

    def archive(self, reason="ticket change"):
        delete_ticket = DeletedTicket(**self.to_dict)
        delete_ticket.delete_reason = reason
        delete_ticket.save()
        self.delete(keep_parents=True)


class DeletedTicket(models.Model):
    delete_on = CreationDateTimeField(editable=False)
    delete_reason = models.CharField(_("Przyczyna skasowania"), max_length=1024, null=False, blank=False)
    code = models.CharField(_("Kod Biletu"), max_length=16, primary_key=True)
    description = models.CharField(_("Opis"), max_length=128, db_index=True, blank=True, null=True)
    hospital = models.ForeignKey(Hospital, verbose_name=_("Szpital"), on_delete=models.CASCADE)
    bed = models.ForeignKey(Bed, verbose_name=_("Łóżko"), on_delete=models.CASCADE, null=True)
    respirator = models.BooleanField(_("Potrzebny Respirator"))
    oxygen = models.BooleanField(_("Potrzebny Tlen"))
    child = models.BooleanField(_("Potrzebne Łóżko Dziecięce"))
    use_respirator = models.BooleanField(_("Użyty Mobilny Respirator"))
    use_oxygen = models.BooleanField(_("Użyty Mobilny Tlen"))
    expiration_date = models.DateTimeField(_("Data Ważności"), null=True, blank=True)
    canceled = models.BooleanField(_("Anulowane"))
    canceled_reason = models.TextField(_("Przyczyna Anulowania"), null=True, blank=True)
    created_on = models.DateTimeField()
    last_modified_on = models.DateTimeField()
    prev = models.ForeignKey("DeletedTicket", null=True, editable=False, on_delete=models.CASCADE)
