from google.cloud import texttospeech
import os

# Set the path to the service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'

def text_to_speech(input_file, output_file):
    # Initialize the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Read the text from the file
    with open(input_file, 'r') as file:
        text = file.read()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code and the voice name
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
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


def list_voices():
    # Initialize the Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Call the API to list voices
    response = client.list_voices()

    # Print available voices
    for voice in response.voices:
        print(f"Name: {voice.name}")
        print(f"Language Codes: {', '.join(voice.language_codes)}")
        print(f"SSML Gender: {voice.ssml_gender}")
        print("")


# list_voices()

# Example usage of text_to_speech
input_file = "input-2.txt"
output_file = "output2.mp3"
text_to_speech(input_file, output_file)
