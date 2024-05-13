import sounddevice as sd
import soundfile as sf
import os
import wave

from gtts import gTTS
from openai import OpenAI

LANG_MAP = {'Spanish': 'es', 'Greek': 'el', 'French': 'fr', 'Chinese': 'cn'}

# Set up OpenAI client
client = OpenAI()
# HOOK language select dropdown should modify target_lang
def translate_text(text, source_lang='en', target_lang='el'):
    try:
        model = "gpt-4"
        response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": "Translate this text to Greek: 'Hello, how are you?'"},],temperature=0,)
        translated_text = response.choices[0].message.content
        return translated_text
    except Exception as e:
        return str(e)

# Set up audio parameters
def record(): # HOOK - record button should call this function
    FS = 44100
    SECONDS = 5
 
    # Record audio
    print("recording...") # Refactor this to be handled by user input buttons
    myrecording = sd.rec(int(SECONDS * FS), samplerate=FS, channels=2) # HOOK stop recordingO
    sd.wait()
    print("finished recording")

    # Save the recorded audio to a WAV file
    sf.write("output.wav", myrecording, FS)

    # HOOK language select dropdown should modify target_lang
def transcribe_and_translate_file(target_lang='el'):# Open the saved WAV file and transcribe it
    with open("output.wav", 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
          model="whisper-1", 
          file=audio_file
        )
    translated = translate_text(transcription, source_lang='en', target_lang=target_lang)
    print(translated)
    return translated        
# HOOK language select dropdown should modify target_lang
def read_translated_aloud(target_lang='el'):
# Convert the text to speech
    tts = gTTS(translated, lang=target_lang)

# Save the audio to a file
    tts.save("output.mp3")

# Play the audio file
    os.system("mpg321 output.mp3")

def main():
    # HOOK language select dropdown should modify target_lang
    target_lang = 'el'
    record()
    transcribe_and_translate_file(target_lang)
    read_translated_aloud(target_lang)


if __name__ == '__main__':
    main()