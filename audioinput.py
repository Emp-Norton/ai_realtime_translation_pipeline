import pyaudio
import os
import wave

from gtts import gTTS
from openai import OpenAI

# Set up OpenAI client
client = OpenAI()

def translate_text(text, source_lang='en', target_lang='el'):
    try:
        model = "gpt-4"
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": "Translate this text to Greek: 'Hello, how are you?'"},],temperature=0,)
        translated_text = response.choices[0].message.content
        return translated_text
    except Exception as e:
        return str(e)

# Set up audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# Set up audio stream
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

print("recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("finished recording")

# Stop and close the stream 
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recorded audio to a WAV file
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

# Open the saved WAV file and transcribe it
with open(WAVE_OUTPUT_FILENAME, 'rb') as audio_file:
    transcription = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
    )
    translated = translate_text(transcription, source_lang='en', target_lang='es')
    print(translated)

# Convert the text to speech
    tts = gTTS(translated, lang='es')

# Save the audio to a file
    tts.save("output.mp3")

# Play the audio file
    os.system("mpg321 output.mp3")
