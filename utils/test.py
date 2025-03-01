from stt import speech_to_text
if __name__ == "__main__":
    transcription  = speech_to_text(r"audio\person_1_output.wav")
    if transcription:
        print(f"Final Transcription: {transcription}")
    else:
        print("No transcription available.")