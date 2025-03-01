import time
import streamlit as st
import pyaudio
import wave
from utils.stt import speech_to_text
from utils.stt2 import speech_to_text2
from agent import agent_executor
from utils.llm_intiate import llm_g
from datetime import datetime
now = datetime.now()
curr_date = now.strftime("%d-%m-%Y")

st.set_page_config(layout="wide")

# Initialize session state variables
if 'person_1_running' not in st.session_state:
    st.session_state.person_1_running = False

if 'person_2_running' not in st.session_state:
    st.session_state.person_2_running = False

if 'helpme_result' not in st.session_state:
    st.session_state.helpme_result = ""

if 'transcript' not in st.session_state:
    st.session_state.transcript = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Custom CSS for colors and styling
st.markdown("""
    <style>
    .main-title {
        color: #1E88E5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .chat-header {
        color: #D32F2F;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .chat-content {
        background-color: #F5F5F5;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .divider {
        border-top: 2px solid #333;
        margin: 10px 0;
    }
    .stButton>button {
        background-color: #2196F3;
        color: white;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }
    </style>
""", unsafe_allow_html=True)

# Layout
st.markdown('<h1 class="main-title">Conversation Helper Agent</h1>', unsafe_allow_html=True)

# Columns for layout
col1, col2 = st.columns(2)

# Function to record audio
def record_audio(filename, format=pyaudio.paInt16, channels=1, rate=44100, chunk=1024, person=1):
    st.write(f"Recording for Person {person} started. Please wait...")
    audio = pyaudio.PyAudio()
    stream = None
    frames = []

    try:
        stream = audio.open(format=format,
                            channels=channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=chunk)

        while (st.session_state.person_1_running if person == 1 else st.session_state.person_2_running):
            data = stream.read(chunk)
            frames.append(data)

    except Exception as e:
        st.error(f"An error occurred while recording: {e}")

    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        audio.terminate()

        if frames:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(audio.get_sample_size(format))
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))
            st.success(f"Recording for Person {person} saved as {filename}")
        else:
            st.warning(f"No audio data was recorded for Person {person}.")

# Function to update the transcript
def update_transcript(person, text):
    if text:
        st.session_state.transcript.append(f"Person {person}: {text}")

# Function to process the conversation
def process_conversation(transcript):
    summary = "Conversation Summary:\n\n" + "\n".join(transcript)
    return summary

# Function to update chat history
def update_chat_history(transcript, helpme_result, agent_result):
    st.session_state.chat_history.append({
        "transcript": transcript.copy(),
        "helpme_result": helpme_result,
        "agent_result": agent_result
    })

# Function to save chat history to a text file
def save_chat_to_txt():
    chat_filename = "chat_history.txt"
    try:
        with open(chat_filename, "w", encoding="utf-8") as file:
            for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
                file.write(f"Chat {i}:\n")
                for line in chat["transcript"]:
                    file.write(f"{line}\n")
                file.write(f"Summarized Question: {chat['agent_result']['question']}\n")
                file.write(f"Source Used: {chat['agent_result']['tool_used']}\n")
                file.write(f"Answer: {chat['agent_result']['answer']}\n")
                file.write("\n" + "="*40 + "\n")
        return chat_filename
    except Exception as e:
        print(f"An error occurred while saving the chat history: {e}")
        return None

# Left Column: Controls
with col1:
    st.subheader("Controls")
    
    if st.button('Press to speak as Person 1', key='person1'):
        if st.session_state.person_1_running:
            st.session_state.person_1_running = False
            st.write("Person 1 Recording stopped.")
            time.sleep(1)
            start_transcription = time.time()
            with st.spinner('Transcribing audio for Person 1...'):
                t1 = speech_to_text("person_1_output.wav")
            transcription_time = time.time() - start_transcription
            st.write(f"Transcription for Person 1 took {transcription_time:.2f} seconds.")
            update_transcript(1, t1)
        else:
            st.session_state.person_1_running = True
            record_audio("person_1_output.wav", person=1)

    if st.button('Press to speak as Person 2', key='person2'):
        if st.session_state.person_2_running:
            st.session_state.person_2_running = False
            st.write("Person 2 Recording stopped.")
            time.sleep(1)
            start_transcription = time.time()
            with st.spinner('Transcribing audio for Person 2...'):
                t2 = speech_to_text2("person_2_output.wav")
            transcription_time = time.time() - start_transcription
            st.write(f"Transcription for Person 2 took {transcription_time:.2f} seconds.")
            update_transcript(2, t2)
        else:
            st.session_state.person_2_running = True
            record_audio("person_2_output.wav", person=2)

    if st.button('Help Me', key='helpme'):
        start_helpme = time.time()
        st.session_state.helpme_result = process_conversation(st.session_state.transcript)
        
        start_question = time.time()
        question = llm_g.invoke(f"Identify the question for the given conversation {st.session_state.transcript} and provide only the question ' ' ")
        question_time = time.time() - start_question
        st.write(f"Question identification took {question_time:.2f} seconds.")

        with st.spinner('Processing the conversation...'):
            start_agent = time.time()
            agent_result = agent_executor.invoke({
                "user_input": question.content,
            })
            print(question.content+curr_date)
            agent_time = time.time() - start_agent
            st.write(f"Agent execution took {agent_time:.2f} seconds.")
        
        helpme_total_time = time.time() - start_helpme
        st.write(f"Total 'Help Me' processing time: {helpme_total_time:.2f} seconds.")
        
        agent_summary = {
            "question": agent_result["output"]["question"],
            "tool_used": agent_result["output"]["tool_used"],
            "answer": agent_result["output"]["answer"]
        }
        update_chat_history(st.session_state.transcript, st.session_state.helpme_result, agent_summary)
        st.session_state.transcript = []  # Reset transcript after processing

# Right Column: Chat History
with col2:
    for line in st.session_state.transcript:
        st.markdown(f"<div class='chat-content'>{line}</div>", unsafe_allow_html=True)
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
            st.subheader("Help Me Press Identified")
            st.markdown(f'<div class="chat-content">{"<br>".join(chat["transcript"])}</div>', unsafe_allow_html=True)
            st.markdown(f"**Summarized Question:** \n\n{chat['agent_result']['question']}")
            st.markdown(f"**Source Used:** \n\n{chat['agent_result']['tool_used']}")
            st.markdown(f"**Answer:**\n\n{chat['agent_result']['answer']}")
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Add the download button at the bottom of the left column
with col1:
    if st.session_state.chat_history:
        chat_filename = save_chat_to_txt()
        with open(chat_filename, "rb") as file:
            st.download_button(
                label="Download Transcript",
                data=file,
                file_name=chat_filename,
                mime="text/plain"
            )
