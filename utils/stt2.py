import os
import wave
from dotenv import load_dotenv
# from websearch import google_search_with_images
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()

# Path to the audio file
API_KEY = os.getenv("DEEPGRAM_API_KEY")

def create_placeholder_audio(AUDIO_FILE):
    """
    Creates a placeholder audio file if the specified audio file doesn't exist.
    The file is a 1-second silent audio file.
    """
    print("Audio file not found. Creating a placeholder audio file...")
    sample_rate = 44100  # 44.1 kHz sample rate
    duration = 1  # 1 second of silence
    n_frames = int(sample_rate * duration)
    silence = bytearray(n_frames * 2)  # 16-bit audio (2 bytes per sample)

    with wave.open(AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(sample_rate)
        wf.writeframes(silence)

    # print(f"Placeholder audio file created at {AUDIO_FILE}")


def speech_to_text2(AUDIO_FILE):
    try:
        # Check if the audio file exists; create it if not
        if not os.path.exists(AUDIO_FILE):
            create_placeholder_audio(AUDIO_FILE)

        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

        # STEP 4: Print and return the transcription
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        # print(f"TRANSCRIPTION: {transcript}")
        return transcript

    except Exception as e:
        # print(f"Exception: {e}")
        return None

# # Example usage
if __name__ == "__main__":
    transcription  = speech_to_text2(r"audio\person_1_output.wav")
    if transcription:
        print(f"Final Transcription: {transcription}")
    else:
        print("No transcription available.")