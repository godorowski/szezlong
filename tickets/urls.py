from django.urls import path
from . import views

urlpatterns = [
    path('<str:bed_id>/create', views.TicketsCreate.as_view(), name='ticket-create-bed'),
    path('<str:hospital_id>/<str:action>/create', views.TicketsCreate.as_view(), name='ticket-create'),
    path('<str:pk>/update', views.TicketsUpdate.as_view(), name='ticket-update'),
    path('<str:pk>/delete', views.TicketsCreate.as_view(), name='ticket-delete'),
    path('<str:hospital_id>/<str:mode>', views.TicketsList.as_view(), name='ticket-list'),
    path('<str:hospital_id>', views.TicketsList.as_view(), name='ticket-list-default'),
    path('', views.hospitals_list, name='ticket-hospitals-list'),
]
