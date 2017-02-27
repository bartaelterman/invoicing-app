from django.contrib import admin
from .models import Client, Invoice, Project, TimeEntry
from admin_views.admin import AdminViews

class ProjectAdmin(AdminViews):
    admin_views = (
        ('Generate Timesheet', 'generate_timesheet'),
        ('Generate Invoice', 'generate_invoice'),
    )

class InvoiceAdmin(admin.ModelAdmin):
    change_form_template = 'admin/invoice_change_form.html'


admin.site.register(Project, ProjectAdmin)

admin.site.register(Client)
admin.site.register(Invoice)
admin.site.register(TimeEntry)