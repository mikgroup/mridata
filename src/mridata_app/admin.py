from django.contrib import admin
from .models import Data, TempData, GeData, PhilipsData, SiemensData, IsmrmrdData

admin.site.register(Data)
admin.site.register(TempData)
admin.site.register(GeData)
admin.site.register(PhilipsData)
admin.site.register(SiemensData)
admin.site.register(IsmrmrdData)
