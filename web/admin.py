from web.models import *
from django.contrib import admin

# Register your models here.
admin.site.register(User)
admin.site.register(UserWallet)
admin.site.register(Contactinfo)
admin.site.register(UserSettings)
admin.site.register(PayHistory)
admin.site.register(AlertVerify)
admin.site.register(UserPassToken)