import csv
import io
from rest_framework import serializers
from core import models as core_models

class UploadedCsvFileSerializer(serializers.ModelSerializer):
    """
    Serializer for handling CSV file uploads.

    This serializer is used to validate and serialize the CSV file uploaded by the user.
    It ensures that the file is correctly received and stored in the ProcessData model.

    Fields:
    - id (UUID): The unique identifier for the uploaded file.
    - csv_file (FileField): The CSV file being uploaded.

    Example Usage:
    ```python
    from core.serializers import UploadedCsvFileSerializer

    data = {'csv_file': uploaded_file}
    serializer = UploadedCsvFileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    ```
    """
    csv_file = serializers.FileField()

    class Meta:
        model = core_models.ProcessData
        fields = ['id', 'csv_file']

    def validate_csv_file(self, file):
        """Ensure the uploaded file is a properly formatted CSV."""

        if not file.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")

        try:
            """
            Use io buffer reader as file is not resent on server, so read by converting it 
            Use file.read().decode('utf-8') InMemoryUploadedFile stores binary data, so we need to decode it first.
            Use io.StringIO(decoded_file) Converts the string content into a file-like object for csv.reader.
            Use file.seek(0) Ensures the file pointer is reset after reading.
            """

            # Code by GPT :)
            file.seek(0)  
            decoded_file = file.read().decode('utf-8')  
            file_data = io.StringIO(decoded_file) 
            reader = csv.reader(file_data)

            required_columns = ['S. No.', 'Product Name', 'Input Image Urls']
            headers = next(reader, None)  # Read only 1st line

            if headers is None:
                raise serializers.ValidationError("The CSV file has no headers.")

            # Normalize headers
            headers = [header.strip().lower() for header in headers]
            required_columns = [col.strip().lower() for col in required_columns]
            
            missing_columns = [col for col in required_columns if col not in headers]

            if missing_columns:
                raise serializers.ValidationError(f"Missing required columns: {', '.join(missing_columns)}")

        except Exception as e:
            raise serializers.ValidationError(f"Error reading CSV file: {str(e)}")

        # If no validation errors, return the file
        return file



class ProcessDataSerializer(serializers.ModelSerializer):
    """
    This serializer used to seralize data for status api
    """
    class Meta:
        model = core_models.ProcessData
        fields = ['id', 'status', 'created_at', 'completed_at', 'message','new_csv_url']
