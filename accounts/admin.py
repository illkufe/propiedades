from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import *

# modelos
class UserProfileInline(admin.StackedInline):
	model = UserProfile

class UserInlineAdmin(UserAdmin):
	inlines = [ UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserInlineAdmin)
admin.site.register(UserType)