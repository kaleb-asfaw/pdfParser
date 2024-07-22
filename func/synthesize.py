from google.cloud import texttospeech
from google.oauth2 import service_account
import os, base64, json

credentials_base64 = os.getenv('GOOGLETTS_CREDENTIALS_BASE64')
if not os.getenv('GOOGLETTS_CREDENTIALS_BASE64'):
    raise EnvironmentError("Did not retrieve Google TTS key from the environment.")

credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
credentials_data = json.loads(credentials_json)

# Create temporary file to store credentials
with open('temp_credentials.json', 'w') as f:
    f.write(credentials_json)

credentials = service_account.Credentials.from_service_account_file('temp_credentials.json')
client = texttospeech.TextToSpeechClient(credentials=credentials)
os.remove('temp_credentials.json')


# writes the audio to a file
def text_to_speech(input_file, output_file):
    # Read the text from the file
    with open(input_file, 'r') as file:
        text = file.read()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code and the voice name
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name = "en-US-Standard-G", 
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE 
    )

    # Select the type of audio file you want
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Write the response to the output file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')


# same as text-to-speech but takes in a String and also automatically stores filename (user given) to func/recordings
def make_mp3(text, filename):
    """
    Converts text to speech and returns the MP3 audio content.

    Args:
    text (str): The text to be converted to speech.
    filename (str): The name of the file to be saved (without extension).

    Returns:
    bytes: The MP3 audio content.
    """
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code and the voice name
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-G", 
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Select the type of audio file you want
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Create the output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'recordings')
    os.makedirs(output_dir, exist_ok=True)


    # Construct the full file path
    output_file = os.path.join(output_dir, f"{filename}.mp3")

    # Write the response to the output file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')

    return response.audio_content

text = "Hello, this is a test."
filename = "test_audio"
make_mp3(text, filename)

# list_voices()

# Example usage of text_to_speech
# input_file = "func/text_files/input.txt"
# output_file = "func/recordings/output3.mp3"
# text_to_speech(input_file, output_file)


# def list_voices():
#     # Call the API to list voices
#     response = client.list_voices()

#     # Print available voices
#     for voice in response.voices:
#         print(f"Name: {voice.name}")
#         print(f"Language Codes: {', '.join(voice.language_codes)}")
#         print(f"SSML Gender: {voice.ssml_gender}")
#         print("")