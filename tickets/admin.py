from django.contrib import admin
from .models import Ticket, DeletedTicket

admin.site.register(Ticket)
admin.site.register(DeletedTicket)
