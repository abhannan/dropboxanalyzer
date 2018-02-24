from django.urls import re_path, path, include
from django.views.generic import RedirectView
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    re_path('^$', views.index, name='home'),
    path('accounts/', include('registration.backends.simple.urls')),
    path('dropbox-auth-start/', views.dropbox_auth_start, name='dropbox-auth-start'),
    path('dropbox-auth-finish/', views.dropbox_auth_finish, name='dropbox-auth-finish'),
    path('api/data/', views.DashboardData.as_view(), name='dashboard-data'),
    path('api/duplicates/', views.get_duplicate_files, name='duplicate-files'),
    path('dashboard/', login_required(views.Dashboard.as_view()), name='dashboard'),

]