from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import Question, Choice

AdminSite.site_header = "Django Polls"

admin.site.register(Question)
admin.site.register(Choice)
