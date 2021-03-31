from django.utils.translation import gettext_lazy as _
from django.db import models
from beret_utils.random_code import Codes

from common import CommonModel

from hospitals.models import Hospital, Specialisation


class Bed(models.Model):
    class Meta:
        ordering = ["localisation", "code"]

    code = models.CharField(_("Kod Łóżka"), max_length=16, primary_key=True)
    localisation = models.CharField(
        _("Lokalizacja"),
        max_length=128,
        db_index=True,
        blank=True,
        help_text=_("Lokalizacja łóżka, np. Paw.B Sala 205, dla poprawnego sortowania należy używać jednego schematu.")
    )
    description = models.CharField(
        _("Opis"),
        max_length=128,
        db_index=True,
        blank=True,
        help_text=_("Wewnętrzny opis łóżka.")
    )
    hospital = models.ForeignKey(Hospital, verbose_name=_("Hospital"), on_delete=models.CASCADE)
    respirator = models.BooleanField(_("Respirator"), default=False)
    oxygen = models.BooleanField(_("Oxygen"), default=False)
    child = models.BooleanField(_("Child"), default=False)
    specialisation = models.ForeignKey(Specialisation, related_name="beds", null=True, on_delete=models.SET_NULL, blank=True)

    def __str__(self):
        return f"{self.code} {self.localisation}" if len(self.localisation) else self.code

    def gen_code(self):
        code_generator = Codes(chars=Codes.DEFAULT_CHARS.upper(), count=Bed.objects.count())
        while True:
            code = f"{self.hospital.code}:{code_generator()}"
            if not Bed.objects.filter(pk=code).count():
                return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.gen_code()
        super().save(*args, **kwargs)
