from django.contrib import admin
from api.models import *

admin.site.register(SplititUser)
admin.site.register(SplititGroup)
admin.site.register(Bill)
admin.site.register(Transaction)
admin.site.register(GroupTransaction)