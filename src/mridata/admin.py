from django.contrib import admin
from .models import Data, TempData, GeData, PhilipsData, SiemensData, IsmrmrdData, \
    Project, Log, GeAwsData, PhilipsAwsData, SiemensAwsData, IsmrmrdAwsData


class DataAdmin(admin.ModelAdmin):
    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter),
        ('uploader', admin.RelatedOnlyFieldListFilter),
    )
    
class TempDataAdmin(admin.ModelAdmin):
    list_filter = (
        ('project', admin.RelatedOnlyFieldListFilter),
        ('uploader', admin.RelatedOnlyFieldListFilter),
    )
    
class LogAdmin(admin.ModelAdmin):
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
    )
    
admin.site.register(Data, DataAdmin)
admin.site.register(GeData, TempDataAdmin)
admin.site.register(GeAwsData, TempDataAdmin)
admin.site.register(PhilipsData, TempDataAdmin)
admin.site.register(PhilipsAwsData, TempDataAdmin)
admin.site.register(SiemensData, TempDataAdmin)
admin.site.register(SiemensAwsData, TempDataAdmin)
admin.site.register(IsmrmrdData, TempDataAdmin)
admin.site.register(IsmrmrdAwsData, TempDataAdmin)
admin.site.register(Project)
admin.site.register(Log, LogAdmin)
