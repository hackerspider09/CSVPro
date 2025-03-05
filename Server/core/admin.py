from django.contrib import admin
from core import models as core_models

# Register your models here.
class ProcessDataAdmin (admin.ModelAdmin):
    list_display = ('id',"status","created_at","completed_at")
admin.site.register(core_models.ProcessData,ProcessDataAdmin)


class ProductDataAdmin (admin.ModelAdmin):
    list_display = ('id',"name")
admin.site.register(core_models.ProductData,ProductDataAdmin)

class ImageDataAdmin (admin.ModelAdmin):
    list_display = ('id',"product_data")
admin.site.register(core_models.ImageData,ImageDataAdmin)
