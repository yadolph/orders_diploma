from django.contrib import admin
from market.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ['username', 'type']
    list_display = ['username', 'type']