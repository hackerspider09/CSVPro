import csv 
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
from core import models as core_models

def validate_headers_utils(process_data):
    """
    This util is used to validate csv file as per static data
    """
    try:
        with open(process_data.csv_file.path, 'r', newline='', encoding="utf-8") as file_data:
            reader = csv.reader(file_data)
            headers = next(reader)  

            # Define the required columns
            required_columns = ['S. No.', 'Product Name', 'Input Image Urls']

            # Normalize headers and required columns (convert to lowercase)
            headers = [header.strip().lower() for header in headers]
            required_columns = [col.strip().lower() for col in required_columns]

            # Check if all required columns are present in the headers
            missing_columns = [col for col in required_columns if col not in headers]

            if missing_columns:
                # If missing columns, set the status to failed and add a message
                process_data.status = 'failed'
                process_data.message = f"Missing required columns: {', '.join(missing_columns)}"
                process_data.save()
                return False
        
        return True
    except Exception as e:
        # Handle other exceptions such as file error
        process_data.status = 'failed'
        process_data.message = f"Error processing file: {str(e)}"
        process_data.save()
        print("Error",e)
        return False
    
    
def create_new_csv_util(process_data):
    """
    This util is used to process csv and compress image 
    Store compressed images in db
    Create new csv 
    """
    process_data.status = "processing"
    process_data.save()


    new_csv_rows = []
    try:
        # Open CSV file
        with open(process_data.csv_file.path, 'r', newline='', encoding="utf-8") as file_data:
            reader = csv.reader(file_data)
            headers = next(reader)  

            # create 1st row for new csv (title)
            new_csv_headers = headers + ['Output Image Urls']
            new_csv_rows.append(new_csv_headers)

            for row in reader:
                # Extract the values from the row
                serial_number, product_name, input_image_urls = row
                input_image_urls = input_image_urls.split(',')

                # Create ProductData for each product
                product_data = core_models.ProductData.objects.create(
                    process_data=process_data,
                    name=product_name
                )

                output_image_urls = []

                # Process Image for each input image url
                for input_url in input_image_urls:
                    input_url = input_url.strip()

                    # Download the image and compress
                    process_image_status = process_image_util(process_data,product_data,input_url)

                    if(process_image_status.get('status')==True):
                        output_image_urls.append(process_image_status.get("output_image_url"))

                # Create new row with old data + output urls
                new_row = row + [', '.join(output_image_urls)]
                new_csv_rows.append(new_row)

            # Once all rows are processed, update ProcessData status
            process_data.status = 'completed'
            process_data.completed_at = timezone.now()
            process_data.save()

        # Generate the new CSV file with the output URLs
        new_csv_filename = f"processed_{process_data.id}.csv"
        new_csv_dir = os.path.join(settings.MEDIA_ROOT, f'csv/output/{process_data.id}')

        # Create the directory if it doesn't exist
        os.makedirs(new_csv_dir, exist_ok=True)

        new_csv_path = os.path.join(new_csv_dir, new_csv_filename)

        # Write to the new CSV file
        with open(new_csv_path, mode='w', newline='', encoding="utf-8") as new_csv_file:
            writer = csv.writer(new_csv_file)
            writer.writerows(new_csv_rows)

        process_data.new_csv_url = f"{settings.SERVER_MEDIA_URL}/csv/output/{process_data.id}/{new_csv_filename}"
        process_data.save()

        return True

    except Exception as e:
        process_data.status = 'failed'
        process_data.message = f"Error processing rows: {str(e)}"
        process_data.save()
        print("Error3",e)
        return False
    

def process_image_util(process_data,product_data,input_url):
    """
    This util is used to get image from url and compress it 
    Store on local machine or cloud storage

    Return:
    {
        dict = {
            status: bool # is image processed or not
            output_image_url: str # url of processed image
        }
    }

    """
    data={
        'status':False
    }
    try:
        # Image compression by GPT
        image_response = requests.get(input_url)
        image = Image.open(BytesIO(image_response.content))
        # Compress the image to 50% of original size
        output_image = image.copy()
        output_image = output_image.resize((int(image.width * 0.5), int(image.height * 0.5)), Image.Resampling.LANCZOS)
        # Create file name and save image locally
        image_filename = os.path.basename(input_url)
        output_image_path = os.path.join(settings.MEDIA_ROOT, f'processed_images/{process_data.id}', image_filename)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
        # Save the compressed image
        output_image.save(output_image_path)

        # Create ImageData object
        image_data = core_models.ImageData.objects.create(
            product_data=product_data,
            input_url=input_url,
            output_url=f'processed_images/{process_data.id}/{image_filename}'  # URL to access compressed image
        )

        data["status"] = True
        data["output_image_url"]=f'{settings.SERVER_MEDIA_URL}/processed_images/{process_data.id}/{image_filename}'

        return data
    except Exception as e:
        print(f"Error processing image {input_url}: {e}")
        return data
        