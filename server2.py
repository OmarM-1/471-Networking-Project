server.py
import socket
from threading import Thread
import os
import random
import boto3
from botocore.exceptions import ClientError
import io

BUFFER_SIZE = 4096
ENC = 'utf-8'
# Define a port range for data connections (configure these in AWS Security Group)
DATA_PORT_MIN = 30000
DATA_PORT_MAX = 40000

# AWS S3 Configuration
S3_BUCKET_NAME = 'cpsc-471'
S3_REGION = 'us-west-1'

class Server:
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)

        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3', region_name=S3_REGION)
            # Test connection
            self.s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            print(f"Connected to S3 bucket: {S3_BUCKET_NAME}")
        except ClientError as e:
            print(f"Error connecting to S3: {e}")
            print("Make sure AWS credentials are configured and bucket exists")
            raise

        self.used_ports = set()
        print(f"Server started on {HOST}:{PORT}")
        print(f"Data port range: {DATA_PORT_MIN}-{DATA_PORT_MAX}")

    def get_data_port(self):
        """Get an available port in the configured range"""










