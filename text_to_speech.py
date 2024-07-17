import pyttsx3
import pyaudio
import wave
import threading

def save_audio(engine, text, output_file):
    # Define the callback to start recording
    def onStart(name):
        print(f'Starting to say: {text}')
        global frames
        frames = []

        def callback(in_data, frame_count, time_info, status):
            global frames
            data = stream.read(frame_count)
            frames.append(data)
            return (data, pyaudio.paContinue)

        nonlocal stream
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=1024,
                        stream_callback=callback)

        stream.start_stream()

    # Define the callback to stop recording
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

    engine.connect('started-utterance', onStart)
    engine.connect('finished-utterance', onEnd)

    engine.save_to_file(text, output_file)
    engine.runAndWait()

if __name__ == "__main__":
    text = "Hello, how are you?"
    output_file = "output.wav"
    engine = pyttsx3.init()

    save_audio(engine, text, output_file)
