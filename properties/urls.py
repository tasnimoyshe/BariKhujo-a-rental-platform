from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('details/<int:id>/', views.property_details, name='property_details'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('post-property/', views.post_property, name='post_property'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-property/<int:id>/', views.delete_property, name='delete_property'),
    
    # নতুন যুক্ত করা হলো
    path('update-status/<int:id>/<str:status>/', views.update_status, name='update_status'),
    path('edit-property/<int:id>/', views.edit_property, name='edit_property'),
]