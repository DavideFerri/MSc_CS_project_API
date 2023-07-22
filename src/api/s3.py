from __future__ import annotations

import datetime

import boto3
import os
import pandas as pd
from dotenv import load_dotenv
import json
from typing import List
import streamlit as st
load_dotenv()


class S3Connector:

    aws_access_key_id: str = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region: str = os.getenv('S3_REGION_NAME')
    aws_bucket_name: str = os.getenv('S3_BUCKET_NAME')
    s3_endpoint_url: str = os.getenv('S3_ENDPOINT_URL') if os.getenv('S3_ENDPOINT_URL') != "" else None
    _instance: S3Connector = None

    def __new__(cls, **kwargs):
        if not cls._instance:
            cls._instance = super(S3Connector, cls).__new__(cls)
            res = boto3.resource(
                aws_access_key_id=S3Connector.aws_access_key_id,
                aws_secret_access_key=S3Connector.aws_secret_access_key,
                service_name='s3', region_name=S3Connector.aws_region,
                endpoint_url=S3Connector.s3_endpoint_url)
            cls._instance.bucket = res.Bucket(S3Connector.aws_bucket_name)
        return cls._instance

    def get_object_ids(self, ownername: str = None, date: datetime.date = None, extensions: list[str] = ['.pdf']) -> List[str]:
        prefix = ""
        if ownername:
            prefix += f"{ownername}/"
            if date:
                prefix += f"{date.strftime('%Y-%m-%d')}/"

        file_names = []
        for obj in self.bucket.objects.filter(Prefix=prefix):
            file_key = obj.key
            if extensions:
                for ext in extensions:
                    if file_key.endswith(ext):
                        file_names.append(file_key)
                        break
            else:
                file_names.append(file_key)

        return file_names

    def get_object(self, object_id: str) -> bytes | None:
        try:
            s3_object = self.bucket.Object(object_id)
            response = s3_object.get()
            file_content = response['Body'].read()
            return file_content
        except Exception as e:
            # Handle exceptions accordingly (e.g., file not found, permissions issue, etc.)
            print(f"Error while retrieving file: {e}")
            return None

    def add_doc(self, file, document_id: str) -> None:
        # Upload the file to S3 bucket
        self.bucket.upload_fileobj(
            file.file,
            document_id,)
        return None
