import boto3
s3 = boto3.client('s3')
bucket_name = "YOUR-BUCKET-NAME"
directory_name = "DIRECTORY/THAT/YOU/WANT/TO/CREATE" #it's name of your folders
s3.put_object(Bucket=bucket_name, Key=(directory_name+'/'))