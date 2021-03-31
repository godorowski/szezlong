from django.urls import path
from . import views

urlpatterns = [
    path('<str:hospital_id>/create', views.BedsCreate.as_view(), name='beds-create'),
    path('<str:pk>/update', views.BedsUpdate.as_view(), name='beds-update'),
    path('<str:pk>/delete', views.BedsDelete.as_view(), name='beds-delete'),
    path('<str:hospital_id>/<str:action>', views.BedsList.as_view(), name='beds-list-action'),
    path('<str:hospital_id>', views.BedsList.as_view(), name='beds-list'),
]
