from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls import include,url
from django.contrib.auth import views as auth_views
from django.conf.urls import include,url

urlpatterns = [
    path('', views.index, name='index'),
    path('register_merchant', views.register_merchant, name='register_merchant'),
    path('login_merchant', views.login_merchant, name='login_merchant'),
    path('merchant', views.merchant_dashboard, name='merchant'),
    path('logout', views.logout_user, name='logout'),
    path('reset_password', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name="activate"),

    path('add_coaching', views.add_coaching, name='add_coaching'),
    path('add_coaching_metadata', views.add_coaching_metadata, name='add_coaching_data'),
    path('add_branch', views.add_branch, name='add_branch'),
    path('add_address' , views.add_address, name='add_address'),
    path('add_course', views.add_course, name='add_course'),
    path('add_batch', views.add_batch, name='add_batch'),
    path('add_faculty', views.add_faculty, name='add_faculty'),
    path('merchant_filter', views.merchant_filter_coaching, name='merchant_filter'),
    path('update_page', views.update_page, name='update_page'),
    path('add_geolocation', views.add_geolocation, name='add_geolocation'),

    path('update_coaching', views.update_coaching, name='update_coaching'),
    path('update_coaching_metadata', views.update_coaching_metadata, name='update_coaching_data'),
    path('update_branch/<str:id>', views.update_branch, name='update_branch'),
    path('update_address/<str:id>' , views.update_address, name='update_address'),
    path('update_course/<str:id>', views.update_course, name='update_course'),
    path('update_batch/<str:id>', views.update_batch, name='update_batch'),
    path('update_faculty/<str:id>', views.update_faculty, name='update_faculty'),
    path('update_geolocation<str:id>', views.update_geolocation, name='update_geolocation'),
]
