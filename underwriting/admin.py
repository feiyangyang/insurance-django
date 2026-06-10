from django.contrib import admin

# Register your models here.
from .models import Customer, Policy, UnderwritingTask, AuditLog

admin.site.register(Customer)
admin.site.register(Policy)
admin.site.register(UnderwritingTask)
admin.site.register(AuditLog)