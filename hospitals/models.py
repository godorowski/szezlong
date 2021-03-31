from django.utils.translation import gettext_lazy as _
from django.db import models

from common import CommonModel
from config import attentions, expires, available, children_available

class Specialisation(CommonModel):
    name = models.CharField(_("Nazwa Specjalizacji/Oddziału"), max_length=255)

    def __str__(self):
        return self.name


class Hospital(models.Model):
    code = models.CharField(_("Kod Szpitala"), max_length=16, primary_key=True)
    name = models.CharField(_("Nazwa Szpitala"), max_length=255)
    address = models.TextField(_("Adres Szpitala"), blank=True)
    specialisations = models.ManyToManyField(Specialisation, verbose_name=_("Dostępne Specjalizacje"), related_name="hospitals", blank=True)
    respirators = models.IntegerField(_("Mobilne Respiratory"), default=0)
    oxygens = models.IntegerField(_("Mobilny Tlen"), default=0)

    @property
    def total_beds(self):
        return self.bed_set.count()

    @property
    def respirator_set(self):
        return self.bed_set.filter(respirator=True)

    @property
    def total_respirators(self):
        return min(self.respirator_set.count() + self.respirators, self.total_beds)

    @property
    def oxygen_set(self):
        return self.bed_set.filter(oxygen=True, respirator=False)

    @property
    def total_oxygens(self):
        return min(self.oxygen_set.count() + self.oxygens, self.total_beds)

    def available(self, queryset=None):
        queryset = queryset or self.bed_set
        return available(queryset)

    @property
    def available_beds(self):
        return self.available().count()

    @property
    def available_respirators(self):
        return self.available(self.respirator_set).count() \
            + self.oxygens - self.ticket_set.filter(use_respirator=True, bed__isnull=False).count()

    @property
    def available_oxygens(self):
        return self.available(self.oxygen_set).count() \
            + self.oxygens - self.ticket_set.filter(use_oxygen=True, bed__isnull=False).count()

    def expires(self, queryset=None):
        queryset = queryset or self.ticket_set
        return expires(queryset)

    @property
    def total_expires(self):
        return self.expires().count()

    def expires_respirator_set(self):
        return self.expires().filter(bed__isnull=False, bed__respirator=True).prefetch_related('bed')

    @property
    def expires_respirators(self):
        return self.expires().filter(bed__isnull=False, bed__respirator=True).count()

    @property
    def expires_oxygens(self):
        return self.expires().filter(bed__isnull=False, bed__respirator=False, bed__oxygen=True).count()

    def attentions(self, queryset=None):
        queryset = queryset or self.ticket_set
        return attentions(queryset)

    @property
    def total_attentions(self):
        return self.attentions().count()

    @property
    def attentions_respirators(self):
        return self.attentions().filter(bed__isnull=False, bed__respirator=True).count()

    @property
    def attentions_oxygens(self):
        return self.attentions().filter(bed__isnull=False, bed__respirator=False, bed__oxygen=True).count()

    def children_set(self, queryset=None):
        queryset = queryset or self.bed_set
        return queryset.filter(child=True)

    @property
    def total_children(self):
        return self.children_set().count()

    def children_available(self, queryset=None):
        return children_available(self.children_set(queryset))

    @property
    def available_children(self):
        return self.children_available().count()

    @property
    def available_children_respirators(self):
        return self.children_available(self.respirator_set).count() \
            + self.oxygens - self.ticket_set.filter(use_respirator=True, bed__isnull=False).count()

    @property
    def available_children_oxygens(self):
        return self.children_available(self.oxygen_set).count() \
            + self.oxygens - self.ticket_set.filter(use_oxygen=True, bed__isnull=False).count()

    def __str__(self):
        return ":".join((self.code, self.name))
