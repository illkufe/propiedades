from django.contrib import admin
from .models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

# Modelos
class UserProfileInline(admin.StackedInline):
	model = UserProfile

class UserProfileAdmin(UserAdmin):
	inlines = [ UserProfileInline, ]

admin.site.unregister(User)
admin.site.register(User, UserProfileAdmin)
