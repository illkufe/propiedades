"""lease URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from lease import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^avatar/', include('avatar.urls')),

    url(r'^', include('accounts.urls', namespace="accounts")),
    url(r'^', include('viewer.urls')),
    url(r'^', include('administrador.urls')),
    url(r'^', include('activos.urls')),
    url(r'^', include('locales.urls')),
    url(r'^', include('contrato.urls')),
    url(r'^', include('conceptos.urls')),
    url(r'^', include('procesos.urls')),
    url(r'^', include('operaciones.urls')),
    url(r'^', include('notificaciones.urls')),
    url(r'^', include('reporteria.urls')),
    url(r'^', include('facturacion.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
