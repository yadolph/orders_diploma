from django.contrib import admin

from market.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass