import pyttsx3
from pydub import AudioSegment
import os


# print("HERE", pyaudio.__version__)
def save_audio(engine, text, output_file):
    # Define the callback to start recording
    def onStart(name):
        print(f'Starting to say: {text}')
        global frames
        frames = []

    # Define a temporary file for pyttsx3 to save the audio
    temp_file = "temp_output.wav"

    try:
        # Save text to speech in the temporary file
        engine.save_to_file(text, temp_file)
        engine.runAndWait()

        # Load the temporary file
        audio = AudioSegment.from_file(temp_file, format="wav")

        # Apply some smoothing effects (optional)
        audio = audio.fade_in(50).fade_out(200)

        # Export the audio to the desired output file
        audio.export(output_file, format="wav")
        
        print(f"Audio saved to: {output_file}")

    except Exception as e:
        print(f"Error saving audio: {e}")

    # finally:
    #     # Clean up: remove the temporary file if it exists
    #     if os.path.exists(temp_file):
    #         os.remove(temp_file)

if __name__ == "__main__":
    text = "To be, or not to be, that is the question: Whether tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: tis a consummation Devoutly to be wishd. To die, to sleep; To sleep, perchance to dream—ay, theres the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil,"
    output_file = "output.wav"
    engine = pyttsx3.init()

    # Set desired speech rate, volume, and voice
    speech_rate = 150  # You can adjust this value to increase or decrease the speed
    volume = 1.0  # You can adjust the volume (0.0 to 1.0)
    voices = engine.getProperty('voices')
    voice_id = "english"  # You can set this to a specific voice ID
    for voice in voices:
        print(voice.id)

    print(f"Selected voice: {voice_id}")
    save_audio(engine, text, output_file, voice_id, rate=speech_rate, volume=volume)


# import pyttsx3
# from pydub import AudioSegment
# from pydub.playback import play
# import os

# def save_audio(engine, text, output_file, voice_id, rate=150, volume=1.0):
#     # Set the speech rate
#     engine.setProperty('rate', rate)
#     # Set the volume
#     engine.setProperty('volume', volume)
#     # Set the voice if provided
#     # if voice_id:
#     #     engine.setProperty('voice', voice_id)
#     engine.setProperty('voice', voice_id)

#     # Define a temporary file for pyttsx3 to save the audio
#     temp_file = "tempy_output.wav"

#     # Save text to speech in the temporary file
#     engine.save_to_file(text, temp_file)
#     engine.runAndWait()

#     # Load the temporary file
#     audio = AudioSegment.from_wav(temp_file)

#     # Apply some smoothing effects
#     audio = audio.fade_in(50).fade_out(200)

#     # Export the audio to the desired output file
#     audio.export(output_file, format="wav")

#     # Remove the temporary file
#     # os.remove(temp_file)

# if __name__ == "__main__":
#     text = "YO MAMA SO FAT"
#     # text = "To be, or not to be, that is the question: Whether tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: tis a consummation Devoutly to be wishd. To die, to sleep; To sleep, perchance to dream—ay, theres the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil,"
#     output_file = "output.wav"
#     engine = pyttsx3.init()

#     # Set desired speech rate, volume, and voice
#     speech_rate = 150  # You can adjust this value to increase or decrease the speed
#     volume = 1.0  # You can adjust the volume (0.0 to 1.0)
#     voices = engine.getProperty('voices')
#     voice_id = voices[0].id  # You can set this to a specific voice ID

#     # Get available voices
#     print(f"selected voice: {voice_id}")

#     # selected_voice_id = None
#     # for voice in voices:
#     #     if "english-north" in voice.name.lower():
#     #         selected_voice_id = voice.id
#     #         break



#     # Optionally, select a specific voice by ID
#     # voice_id = voices[0].id  # Example: select the first voice

#     save_audio(engine, text, output_file, voice_id, rate=speech_rate, volume=volume)


# import pyttsx3
# from pydub import AudioSegment
# from pydub.playback import play
# import os

# def save_audio(engine, text, output_file, rate=150):
#     # Set the speech rate
#     engine.setProperty('rate', rate)
    
#     # Define a temporary file for pyttsx3 to save the audio
#     temp_file = "temp_output.wav"
    
#     # Save text to speech in the temporary file
#     engine.save_to_file(text, temp_file)
#     engine.runAndWait()
    
#     # Load the temporary file
#     audio = AudioSegment.from_wav(temp_file)
    
#     # Export the audio to the desired output file
#     audio.export(output_file, format="wav")
    
#     # Remove the temporary file
#     os.remove(temp_file)

# if __name__ == "__main__":
#     # text = "The middle ages were a period characterized by high religiosity, deep adherence to feudal hierarchies, and limited economic growth"
#     # text = "The quick brown fox jumps over the lazy dog"
#     text = "To be, or not to be, that is the question: Whether tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them. To die—to sleep, No more; and by a sleep to say we end The heart-ache and the thousand natural shocks That flesh is heir to: tis a consummation Devoutly to be wishd. To die, to sleep; To sleep, perchance to dream—ay, theres the rub: For in that sleep of death what dreams may come, When we have shuffled off this mortal coil,"
#     output_file = "output.wav"
#     engine = pyttsx3.init()

#     # Set desired speech rate
#     speech_rate = 150  # You can adjust this value to increase or decrease the speed
#     save_audio(engine, text, output_file, rate=speech_rate)
