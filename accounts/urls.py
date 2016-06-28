# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

	url(r'^usuarios/list$', views.UsuarioList.as_view(), name='usuario_list'),
	url(r'^usuarios/new$', views.UsuarioNew.as_view(), name='usuario_new'),
	url(r'^usuarios/delete/(?P<pk>\d+)$', views.UsuarioDelete.as_view(), name='usuario_delete'),
	url(r'^usuarios/update/(?P<pk>\d+)$', views.UsuarioUpdate.as_view(), name='usuario_update'),

	url(r'^login/$', views.user_login, name='user_login'),
	url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name="logout"),

	url(r'^profile$', views.profile, name='profile'),
	url(r'^update-profile$', views.update_profile, name='update_profile'),
	
	url(r'^update-password/(?P<pk>\d+)$', views.update_password, name='update_password_id'),
	url(r'^update-password', views.update_password, name='update_password'),

]


# handler404 = 'views.custom_404'
# handler500 = 'views.custom_500'
# handler403 = 'views.custom_403'
# handler400 = 'views.custom_400'