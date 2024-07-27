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

def upload_text(user_id, filename, summary_text):
    (
    supabase.table("summary_text")
    .insert({"user_id": user_id, "text": summary_text, "filename": filename})
    .execute()
    )
    return "success"

def fetch_text(user_id, filename):
    """
    response format
    {
        "data": [
            { "text": "blahalbkha" },
            { "text": "blajshfjhw" },
        ],
        "count": null
    }
    """
    response = (
    supabase.table("summary_text")
    .select("text")
    .eq("user_id", user_id)
    .eq("filename", filename)
    .execute()
    )
    if response.data:
        return response.data[0]
    else:
        raise ValueError("No text found for the given user_id and filename.")

    
def fetch_audio(user_id, mp3_filename):
    bucket_name = "mp3"
    file_path = f"{user_id}/{mp3_filename}"

    try:
        response = supabase.storage.from_(bucket_name).download(file_path)
        return response
    except Exception as e:
        raise ValueError(f"Error fetching from Supabase Storage: {e}")
    


def get_mp3_file_names(user_id):
    bucket_name = "mp3"
    folder_path = f"{user_id}/"

    try:
        response = supabase.storage.from_(bucket_name).list(folder_path)

        if isinstance(response, dict) and "error" in response:
            raise ValueError(f"Error listing files in Supabase Storage: {response['error']['message']}")

        # Extract file names from the response
        file_names = [file['name'] for file in response if file['name'].endswith('.mp3')]
        return file_names

    except Exception as e:
        raise ValueError(f"Error fetching file names from Supabase Storage: {e}")
    

if __name__ == "__main__":
    #print(fetch_audio(1,"1721963765.mp3"))
    #print(fetch_text(3, "hello world"))
    pass