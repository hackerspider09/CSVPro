from celery import shared_task
from core import models as core_models
import csv
import os
import requests
from io import BytesIO
from PIL import Image
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .utils import *

@shared_task
def process_csv_file(process_id):
    """
    This task is used to process file async
    and create new csv file
    """
    print(f"Processing file: {process_id}")

    # Retrieve ProcessData object by ID
    try:
        process_data = core_models.ProcessData.objects.get(id=process_id)
    except Exception as e:
        print("Error",e)
        return

    # Open the CSV file and validate it
    is_csv_header_valid = validate_headers_utils(process_data)
    if(not is_csv_header_valid):
        return

    # If the file is valid, continue processing and create file
    is_file_created = create_new_csv_util(process_data)
    if(is_file_created):
        # perfrom webhooks logic or logs the entry or just leave it :) 
        print("File is created")
    else:
        print("Error in file creation")

    return
    







