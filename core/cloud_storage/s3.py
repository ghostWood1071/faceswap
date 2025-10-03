import boto3
import os
from urllib.parse import quote
import app_settings

class S3Service:
    def __init__(self, bucket_name, region="us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        self.s3 = boto3.client("s3", region_name=region)
        self.endpoint = f"https://{bucket_name}.s3.{region}.amazonaws.com"

    def list_objects(self, prefix=""):
        paginator = self.s3.get_paginator('list_objects_v2')
        result = []
        s3 = self.s3
        params = {
            "Bucket": self.bucket_name,
            "Delimiter": "/"
        }

        if prefix:
            params["Prefix"] = prefix if prefix.endswith("/") else prefix + "/"

        response = s3.list_objects_v2(**params)

        result = []

        for cp in response.get("CommonPrefixes", []):
            result.append(cp["Prefix"])

        for obj in response.get("Contents", []):
            if obj["Key"] != params.get("Prefix", ""):
                key = obj['Key']
                url = f"{self.endpoint}/{quote(key)}"
                result.append(url)
        return result


    def upload_file(self, file_path, s3_key):
        self.s3.upload_file(file_path, self.bucket_name, s3_key)
        return f"{self.endpoint}/{quote(s3_key)}"

    def upload_folder(self, folder_path, s3_prefix=""):
        urls = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, folder_path)
                s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")
                url = self.upload_file(full_path, s3_key)
                urls.append(url)
        return urls

    def upload_files(self, files):  # files: list of tuples (file_path, s3_key)
        return [self.upload_file(fp, key) for fp, key in files]

    def delete_file(self, s3_key):
        self.s3.delete_object(Bucket=self.bucket_name, Key=s3_key)
        return f"Deleted {s3_key}"

    def delete_folder(self, prefix):
        paginator = self.s3.get_paginator('list_objects_v2')
        keys = []
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
            for obj in page.get('Contents', []):
                keys.append({'Key': obj['Key']})
        if keys:
            self.s3.delete_objects(Bucket=self.bucket_name, Delete={'Objects': keys})
        return f"Deleted folder {prefix}"
