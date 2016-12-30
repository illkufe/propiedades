from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt


from . import views

urlpatterns = [
	
	# usuarios
	url(r'^usuarios/list/$', views.UsuarioList.as_view(), name='usuario_list'),
	url(r'^usuarios/new/$', views.UsuarioNew.as_view(), name='usuario_new'),
	url(r'^usuarios/delete/(?P<pk>\d+)/$', views.UsuarioDelete.as_view(), name='usuario_delete'),
	url(r'^usuarios/update/(?P<pk>\d+)/$', views.UsuarioUpdate.as_view(), name='usuario_update'),

	# perfil
	url(r'^perfil/$', views.PerfilList.as_view(), name='perfil_list'),

	# update owncloud & password
	url(r'^update-owncloud/', csrf_exempt(views.update_owncloud), name='update_owncloud'),
	url(r'^update-password/(?P<pk>\d+)$/', csrf_exempt(views.update_password), name='update_password_id'),
	url(r'^update-password/', csrf_exempt(views.update_password), name='update_password'),

	# login & logout
	url(r'^login/$', views.user_login, name='user_login'),
	url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name="logout"),

]

# handler404 = 'views.custom_404'
# handler500 = 'views.custom_500'
# handler403 = 'views.custom_403'
# handler400 = 'views.custom_400'
