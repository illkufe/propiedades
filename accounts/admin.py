from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import *

# modelos
class UserProfileInline(admin.StackedInline):
	model = UserProfile

class ConfiguracionOwnCloudInline(admin.StackedInline):
	model = ConfiguracionOwnCloud

class UserInlineAdmin(UserAdmin):
	inlines = [UserProfileInline, ConfiguracionOwnCloudInline]

admin.site.unregister(User)
admin.site.register(User, UserInlineAdmin)
admin.site.register(UserType)