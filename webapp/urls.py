"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from invoicing.views import display_timesheet, generate_timesheet, display_invoice, generate_invoice, get_time_entries

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/timesheet/', display_timesheet, name='timesheet'),
    url(r'^admin/generate_timesheet/', generate_timesheet),
    url(r'^admin/invoice/', display_invoice, name='display_invoice'),
    url(r'^admin/generate_invoice/', generate_invoice),
    url(r'^admin/time_entries/', get_time_entries),
]
