from minio import Minio
import os

class MinioClient:
    """Utility for MinIO file storage operations [cite: 10]"""
    def __init__(self):
        self.client = Minio(
            os.getenv("MINIO_ENDPOINT", "minio:9000"), # [cite: 240]
            access_key=os.getenv("MINIO_ACCESS_KEY", "admin"), # [cite: 241]
            secret_key=os.getenv("MINIO_SECRET_KEY", "admin123"), # [cite: 242]
            secure=False
        )

    def upload_file(self, bucket_name, object_name, file_path):
        """Uploads a file to a specific bucket [cite: 10]"""
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)
        
        self.client.fput_object(bucket_name, object_name, file_path)
        return f"File {object_name} uploaded to {bucket_name}"