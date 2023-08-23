from django.contrib import admin
from .models import Machine

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'user', 'timestamp']
    list_filter = ['status', "user", "timestamp"]
    search_fields = ['name', 'user__username']
    actions = ['make_free', 'make_occupied']
    sortable_by = ['name', "timestamp", 'status']

    def make_free(self, request, queryset):
        queryset.update(status=True, user=None)
    make_free.short_description = "Mark as free"

    def make_occupied(self, request, queryset):
        queryset.update(status=False, user=request.user)
    make_occupied.short_description = "Mark as occupied"
