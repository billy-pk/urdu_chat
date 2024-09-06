# this code uses openai gpt 3.5 turbo and tts-1 models

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from io import BytesIO
from openai import OpenAI
import os
import base64


# Convert the recorded audio to an AudioData object
def bytes_to_audio_data(audio_bytes):
    audio_file = BytesIO(audio_bytes)
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    return audio_data


# Convert voice input to text
def audio_to_text(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        # Convert bytes to AudioData
        audio_data = bytes_to_audio_data(audio_bytes)
        # Use the AudioData to recognize text
        text = recognizer.recognize_google(audio_data, language="ur-PK")
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error with the request; {e}"


# Generate response using OpenAI
def generate_response(text):
    client = OpenAI(api_key = openai_api_key)
    response = client.chat.completions.create(
        model= "gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of USA"},
        {"role": "assistant", "content": "The capital of USA is Washington DC"},
        {"role": "user", "content": text}
        ])
    return response.choices[0].message.content


# text to speech conversion using openai tts_1 model
def text_to_speech_conversion(text):
    """Converts text to audio format message using OpenAI's text-to-speech model - tts-1."""
    if text:  # Check if text is not empty
        client = OpenAI(api_key = openai_api_key)
        response = client.audio.speech.create(
            model="tts-1",  # Model to use for text-to-speech conversion
            voice="fable",  # Voice to use for speech synthesis
            input=text  # Text to convert to speech
        ) # response is a HttpxBinaryResponseContent
        
        audio_data = BytesIO(response.read())  # Read the response into a BytesIO object
        
        return audio_data


def play_audio_auto(audio_data, format="audio/webm"):
    """Embeds the audio in HTML with autoplay enabled."""
    # Encode audio data in base64
    audio_base64 = base64.b64encode(audio_data.getvalue()).decode("utf-8")
    audio_html = f"""
        <audio autoplay>
            <source src="data:{format};base64,{audio_base64}" type="{format}">
            Your browser does not support the audio element.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# Streamlit user interface
st.title('Urdu Voice Assistant')

# prompt for openai api key in sidebar
with st.sidebar:
    openai_api_key = st.text_input("Enter OpenAI API Key", key="api_key", type="password")

# ensure that openi api key was entered
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

audio_bytes = audio_recorder(
    text="Click to record for 5 sec",
    recording_color="red",
    neutral_color="#6aa36f",
    icon_name="microphone-lines",
    icon_size="6x",
    energy_threshold=(-1.0, 1.0),
    pause_threshold=5.0
)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.info("Processing audio...")
    input_text = audio_to_text(audio_bytes)
    st.write("Input Text :", input_text)

    #obtain response from openai 
    response_text = generate_response(input_text)
    st.write(response_text)

    audio_data = text_to_speech_conversion(response_text)

    # If you want to play the audio directly in your Streamlit app:
    st.audio(audio_data, format="audio/webm")


    # Play the audio automatically using HTML
    play_audio_auto(audio_data, format="audio/webm")

    # # Add a play button for manual playback
    # if st.button("Play Audio"):
    #     play_audio_auto(audio_data, format="audio/webm")

    # # Add a reset button to start a new conversation
    # if st.button("Record Again"):
    #     st.query_params.clear()  # This reloads the app and acts as a reset

    
        
    
