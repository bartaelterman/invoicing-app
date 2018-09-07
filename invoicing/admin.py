from django.contrib import admin
from .models import Client, Invoice, InvoiceItem, Profile, Project, TimeEntry
from admin_views.admin import AdminViews


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem


class ProjectAdmin(AdminViews):
    admin_views = (
        ('Generate Timesheet', 'generate_timesheet'),
        ('Generate Invoice', 'generate_invoice'),
    )

class InvoiceAdmin(admin.ModelAdmin):
    # change_form_template = 'admin/invoice_change_form.html'
    inlines = [InvoiceItemInline]


class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('project', 'start', 'duration', 'billable',)
    list_filter = ('project__name',)


admin.site.register(Project, ProjectAdmin)

admin.site.register(Client)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItem)
admin.site.register(Profile)
admin.site.register(TimeEntry, TimeEntryAdmin)