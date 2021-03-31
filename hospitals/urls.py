from django.urls import path
from . import views

urlpatterns = [
    path('create', views.HospitalCreate.as_view(), name='hospital-create'),
    path('<str:pk>/update', views.HospitalUpdate.as_view(), name='hospital-update'),
    path('<str:pk>/delete', views.HospitalDelete.as_view(), name='hospital-delete'),
    path('', views.HospitalList.as_view(), name='hospital-list'),
]
