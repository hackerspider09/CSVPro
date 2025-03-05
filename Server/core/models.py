from django.db import models
import uuid

def getCsvIpPath(instance,filename):
    return str(f"csv/input/{instance.id}/{filename}")
def getCsvOpPath(instance,filename):
    return str(f"csv/output/{instance.id}/{filename}")

status_choice = [('pending','Pending'), ('processing','Processing'), ('completed','Completed'), ('failed','Failed')]

class ProcessData(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    csv_file = models.FileField(upload_to=getCsvIpPath, blank=False, verbose_name="Csv Input")
    status = models.CharField(max_length=20, choices=status_choice, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    message = models.CharField(max_length=200,blank=True,null=True)
    new_csv_url = models.URLField(null=True, blank=True)

    def __str__(self) -> str:
        return str(id)
    
class ProductData(models.Model):
    process_data = models.ForeignKey(ProcessData, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

class ImageData(models.Model):
    product_data = models.ForeignKey(ProductData, on_delete=models.CASCADE)
    input_url = models.URLField()
    output_url = models.URLField(null=True, blank=True)
    