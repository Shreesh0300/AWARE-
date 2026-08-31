import boto3
from botocore import UNSIGNED
from botocore.config import Config
import sys

# Configure anonymous access to AWS S3 (no account required)
s3 = boto3.client('s3', region_name='us-east-1', config=Config(signature_version=UNSIGNED))
bucket_name = 'pmc-oa-opendata'

print("🌐 Connecting to NCBI's AWS S3 Bucket (pmc-oa-opendata)...")

# Creating a BRAND NEW file just for this dataset
output_file = "NCBI_RAW_DATA.txt"
target_files = 500  # Change this number to grab more or less data
downloaded = 0

try:
    # Use paginator to scroll through the massive bucket
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name)

    # Open the new file in 'w' (write) mode to create it fresh
    with open(output_file, 'w', encoding='utf-8') as f:
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                
                # NCBI stores xml, pdf, json, and txt. We ONLY want the raw text!
                if key.endswith('.txt'):
                    # Fetch the text file directly from S3
                    response = s3.get_object(Bucket=bucket_name, Key=key)
                    text_data = response['Body'].read().decode('utf-8')
                    
                    # Write it directly into the master file with a divider
                    f.write(f"\n\n--- NCBI ARTICLE: {key} ---\n\n")
                    f.write(text_data)
                    
                    downloaded += 1
                    
                    # Terminal progress bar (overwrites the same line)
                    sys.stdout.write(f"\r📥 Streamed {downloaded}/{target_files} articles directly into {output_file}")
                    sys.stdout.flush()
                    
                    # Stop once we hit the target
                    if downloaded >= target_files:
                        print(f"\n\n✅ Boom! {target_files} articles successfully streamed into {output_file}.")
                        print("Ready to run your cleaning script on the new file!")
                        sys.exit(0)

except Exception as e:
    print(f"\n🚨 AWS S3 Error: {e}")