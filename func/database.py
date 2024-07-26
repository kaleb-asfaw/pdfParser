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
    try:
        response = supabase.storage.create_bucket(bucket_name)
    except:
        raise ValueError("Error creating Supabase Storage bucket: " + response["error"]["message"])
        
def upload_audio(user_id, mp3_filename, mp3_data):
    bucket_name = "mp3"
    response = supabase.storage.list_buckets()
    file_path = f"{user_id}/{mp3_filename}"

    if not response or not any(bucket.name == bucket_name for bucket in response):
        create_bucket(bucket_name)

    try:
        response = supabase.storage.from_(bucket_name).upload(file_path, mp3_data)
    except:
        raise ValueError("Error uploading to Supabase Storage: " + response["error"]["message"])


    
def fetch_audio(user_id, mp3_filename):
    bucket_name = "mp3"
    file_path = f"{user_id}/{mp3_filename}"

    try:
        response = supabase.storage.from_(bucket_name).download(file_path)
        return response
    except Exception as e:
        raise ValueError(f"Error fetching from Supabase Storage: {e}")

if __name__ == "__main__":
    print(fetch_audio(1,"1721963765.mp3"))