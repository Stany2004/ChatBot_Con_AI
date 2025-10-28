"""Entrypoint for the package's UI with Gemini support."""

import os
from pathlib import Path
import tempfile
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
from fpdf import FPDF
import pygame

from pyrobbot.chat_config_new import ChatConfig
from pyrobbot.chat_new import Chat

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


def text_to_speech(text: str) -> str:
    """Convert text to speech and return the path to the audio file."""
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        return fp.name


def play_audio(file_path: str):
    """Play audio file using pygame."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()


def speech_to_text() -> Optional[str]:
    """Convert speech to text using microphone input."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now")
        try:
            audio = recognizer.listen(source, timeout=5)
            st.info("Processing speech...")
            return recognizer.recognize_google(audio)
        except (sr.UnknownValueError, sr.RequestError) as e:
            st.error(f"Error recognizing speech: {str(e)}")
            return None


def export_to_pdf(messages):
    """Export chat history to PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Chat History", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    
    # Add messages
    for msg in messages:
        # Add role as header
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"{msg['role'].title()}:", ln=True)
        # Add content
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=msg['content'])
        pdf.ln()
    
    # Save PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as fp:
        pdf.output(fp.name)
        return fp.name


def run_app():
    """Create and run the Gemini-powered chat application."""
    st.set_page_config(
        page_title="PyRobBot - Gemini",
        page_icon=":speech_balloon:",
        layout="wide"
    )

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat" not in st.session_state:
        api_key = os.getenv('GOOGLE_API_KEY')
        config = ChatConfig(
            provider="gemini",
            gemini_config={"api_key": api_key}
        )
        st.session_state.chat = Chat(config=config)

    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stButton button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar for settings
    with st.sidebar:
        st.title("Settings")
        api_key = st.text_input("Enter Gemini API Key", type="password")
        if api_key:
            config = ChatConfig(
                provider="gemini",
                gemini_config={"api_key": api_key}
            )
            st.session_state.chat = Chat(config=config)
        
        # Voice Input Button
        if st.button("🎤 Voice Input"):
            user_input = speech_to_text()
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.chat.send_message(user_input)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        # Convert response to speech
                        audio_file = text_to_speech(response)
                        play_audio(audio_file)
                        os.unlink(audio_file)  # Clean up
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Export to PDF button
        if st.session_state.messages and st.button("📄 Export Chat to PDF"):
            pdf_path = export_to_pdf(st.session_state.messages)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download Chat History (PDF)",
                    data=f.read(),
                    file_name="chat_history.pdf",
                    mime="application/pdf"
                )
            os.unlink(pdf_path)  # Clean up

    # Main chat interface
    st.title("PyRobBot - Powered by Gemini AI")

    # Messages are already initialized at the start

    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant":
                # Add play button for assistant messages
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    if st.button("🔊", key=f"play_{i}"):
                        audio_file = text_to_speech(message["content"])
                        play_audio(audio_file)
                        os.unlink(audio_file)  # Clean up

    # Chat input
    if prompt := st.chat_input():
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat.send_message(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    run_app()