import pyttsx3
import pyaudio
import wave

def save_audio(engine, text, output_file, rate=50):
    # Initialize global variables
    global frames
    global stream
    global p

    frames = []

    def onStart(name):
        print(f'Starting to say: {text}')
        # Set up the audio stream
        def callback(in_data, frame_count, time_info, status):
            data = stream.read(frame_count)
            frames.append(data)
            return (data, pyaudio.paContinue)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                stream_callback=callback)

        stream.start_stream()

    def onEnd(name, completed):
        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(output_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))

        print(f'Saving audio to: {output_file}')

    # set voice speed 
    engine.setProperty('rate', rate)

    # Connect callbacks
    engine.connect('started-utterance', onStart)
    engine.connect('finished-utterance', onEnd)

    # Save text to speech
    engine.save_to_file(text, output_file)
    engine.runAndWait()

if __name__ == "__main__":
    text = "Hello, how are you?"
    output_file = "output.wav"
    engine = pyttsx3.init()

    save_audio(engine, text, output_file)
