from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('details/<int:id>/', views.property_details, name='property_details'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    
    # আপনার কাস্টম লগ-আউট (এটিই রাখা হলো)
    path('logout/', views.logout_user, name='logout'),
    
    path('post-property/', views.post_property, name='post_property'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-property/<int:id>/', views.delete_property, name='delete_property'),
    
    # নতুন যুক্ত করা হলো
    path('update-status/<int:id>/<str:status>/', views.update_status, name='update_status'),
    path('edit-property/<int:id>/', views.edit_property, name='edit_property'),
    path('settings/', views.settings_page, name='settings'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('property/<int:id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('property/<int:id>/report/', views.report_property, name='report_property'),
    path('property/<int:id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

]  