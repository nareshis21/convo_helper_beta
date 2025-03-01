import os
import time
from groq import Groq
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from dotenv import load_dotenv
load_dotenv()

# Paths to the audio file
filename = r"C:\Users\Naresh Kumar Lahajal\Desktop\CONV_BETA\person_1_output.wav"

# Groq transcription function
def transcribe_with_groq(filename):
    try:
        client = Groq()
        start_time = time.time()
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                language="en",
                response_format="verbose_json",
            )
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("\nGroq Transcription:")
        print(f"TRANSCRIPTION: {transcription.text}")
        print(f"Time taken for Groq transcription: {elapsed_time:.2f} seconds")
        return transcription.text, elapsed_time
    except Exception as e:
        print(f"Groq Exception: {e}")
        return None, None

# Deepgram transcription function
def transcribe_with_deepgram(filename):
    try:
        deepgram = DeepgramClient()
        start_time = time.time()
        with open(filename, "rb") as file:
            buffer_data = file.read()
        payload: FileSource = {"buffer": buffer_data}
        options = PrerecordedOptions(model="nova-2", smart_format=True)
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("\nDeepgram Transcription:")
        print(f"TRANSCRIPTION: {transcript}")
        print(f"Time taken for Deepgram transcription: {elapsed_time:.2f} seconds")
        return transcript, elapsed_time
    except Exception as e:
        print(f"Deepgram Exception: {e}")
        return None, None

if __name__ == "__main__":
    # Transcribe using Groq
    groq_text, groq_time = transcribe_with_groq(filename)
    
    # Transcribe using Deepgram
    deepgram_text, deepgram_time = transcribe_with_deepgram(filename)

    # Summary
    print("\nSummary:")
    if groq_text:
        print(f"Groq Transcription: {groq_text}")
        print(f"Groq Time: {groq_time:.2f} seconds")
    if deepgram_text:
        print(f"Deepgram Transcription: {deepgram_text}")
        print(f"Deepgram Time: {deepgram_time:.2f} seconds")
