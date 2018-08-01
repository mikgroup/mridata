from django.contrib import admin
from .models import Data, TempData, GeData, PhilipsData, SiemensData, IsmrmrdData, Project

admin.site.register(Data)
admin.site.register(TempData)
admin.site.register(GeData)
admin.site.register(PhilipsData)
admin.site.register(SiemensData)
admin.site.register(IsmrmrdData)
admin.site.register(Project)
admin.site.register(Messages)
