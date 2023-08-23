from django.urls import path
from . import views

urlpatterns = [
    path('', views.machine_list, name='machine_list'),
    path('<int:machine_id>/', views.machine_detail, name='machine_detail'),
    path('<int:machine_id>/book/', views.book_machine, name='book_machine'),
    path('<int:machine_id>/unbook/', views.unbook_machine, name='unbook_machine'),
]
