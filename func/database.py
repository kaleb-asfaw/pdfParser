import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def create_bucket(bucket_name):
    headers = {
        'Authorization': f'Bearer {key}',
        'apikey': key
    }
    response = supabase.storage.create_bucket(bucket_name)
    # if response.get("error"):
        # raise ValueError("Error creating Supabase Storage bucket: " + response["error"]["message"])
        
def upload_audio(user_id, mp3_filename, mp3_data):
    print(user_id)
    bucket_name = f"mp3"
    response = supabase.storage.list_buckets()
    print("RESPONSE:", response)
    if not response or not any(bucket.name == bucket_name for bucket in response):
        print("HERE")
        create_bucket(bucket_name)
    
    file_path = f"{user_id}/{mp3_filename}"
    
    # Upload MP3 file to Supabase Storage directly
    response = supabase.storage.from_(bucket_name).upload(file_path, mp3_data)
    # if response.get("error"):
        # raise ValueError("Error uploading to Supabase Storage: " + response["error"]["message"])


    

def fetch_audio(user_id, mp3_filename):
    pass