from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


from core import models as core_models
from core import serializers as core_serializers
from core import tasks as core_tasks
# Create your views here.

class CSVUploadView(APIView):
    """
    API endpoint for uploading a CSV file.

    This endpoint allows users to upload a CSV file, which will be stored on the server. 
    After a successful upload, it returns a unique ID for tracking the processing status.
    The uploaded file is then processed asynchronously using Celery.

    Request:
    - Method: POST
    - Body Parameters:
        - csv_file: The CSV file to be uploaded.
    
    Response:
    - Success (201 Created):
        {
            "message": "File Uploaded.",
            "id": "1a1ff9b9-fa48-4ee0-a160-6864e5c10306"
        }
    - Failure (400 Bad Request): If the CSV file is invalid or missing.

    Processing:
    - The uploaded file is stored in the database.
    - A background Celery task (process_csv_file) is triggered to process the file asynchronously.
    """
    def post(self, request, *args, **kwargs):
        
        serializer = core_serializers.UploadedCsvFileSerializer(data=request.data)
        
        if serializer.is_valid():
            file = serializer.validated_data['csv_file']
                                    
            uploaded_file = core_models.ProcessData.objects.create(csv_file=file)

            message = {
                "message" : 'File Uploaded.',
                "id" : uploaded_file.id
            }

            core_tasks.process_csv_file.delay(uploaded_file.id)
            return Response(message, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProcessDataStatusView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving the status of a CSV processing task.

    This endpoint allows users to check the status of an uploaded CSV file 
    processing task by providing the unique ID received during upload.

    Request:
    - Method: GET
    - URL: /core/v1/status/{id}/
    - Path Parameters:
        - id (UUID): The unique identifier of the processing task.

    Response:
    - Success (200 OK):
        {
            "id": "1a1ff9b9-fa48-4ee0-a160-6864e5c10306",
            "status": "completed",
            "created_at": "2025-03-05T11:22:17.517219Z",
            "completed_at": "2025-03-05T11:22:19.098155Z",
            "message": null,
            "new_csv_url": "http://localhost:8000/media/csv/output/1a1ff9b9-fa48-4ee0-a160-6864e5c10306/processed_1a1ff9b9-fa48-4ee0-a160-6864e5c10306.csv"
        }
    - Failure (404 Not Found): If the provided ID does not exist.

    """
    queryset = core_models.ProcessData.objects.all()
    serializer_class = core_serializers.ProcessDataSerializer
    lookup_field = 'id'  