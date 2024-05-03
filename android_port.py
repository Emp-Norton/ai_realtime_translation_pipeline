import sounddevice as sd
import soundfile as sf
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
SAMPLE_RATE = 44100
CHANNELS = 2
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

print("recording...")
myrecording = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
sd.wait()
print("finished recording")

# Save the recorded audio to a WAV file
sf.write(WAVE_OUTPUT_FILENAME, myrecording, SAMPLE_RATE)

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
