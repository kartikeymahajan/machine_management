from django.urls import path
from . import views, admin
from .views import CustomLogoutView
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('', views.machine_list, name='machine_list'),
    path('admin_redirect/', views.admin_redirect, name='admin_redirect'),
    path('<int:machine_id>/', views.machine_detail, name='machine_detail'),
    path('<int:machine_id>/book/', views.book_machine, name='book_machine'),
    path('<int:machine_id>/extend_booking/', views.extend_booking, name='extend_booking'),
    path('<int:machine_id>/unbook/', views.unbook_machine, name='unbook_machine'),
    path('<int:machine_id>/edit_notepad/', views.edit_notepad, name='edit_notepad'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', views.profile_view, name='profile')
]
