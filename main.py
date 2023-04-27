import gradio as gr
import openai
from decouple import config
import os
import win32com.client
import pythoncom

openai.api_key = config("OPENAI_API_KEY")

# The Models Job or role
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
]

language = 'en'

def play_welcome_message():
    welcome_message = "Welcome to the voice assistant. You can ask me anything."
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Speak(welcome_message)

# Main method goes here
def decipher(audio=None, text=None):
    global messages

    if audio:
        # Using openAI's speech to text model
        audio_file = open(audio, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        user_message = transcript["text"]
    else:
        user_message = text

    messages.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    system_message = response["choices"][0]["message"]["content"]
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    speaker.Speak(system_message)
    messages.append({"role": "assistant", "content": system_message},)

    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    return chat_transcript

# Use custom styles sheet
with open("custom_styles.css", "r") as css_file:
    custom_css = css_file.read()

interface = gr.Interface(
    fn=decipher,
    inputs=[
        gr.Audio(source="microphone", type="filepath", label="Audio"),
        gr.Textbox(lines=2, placeholder="Type your question here", label="Type your question")
    ],
    outputs="text",
    css=custom_css,
    title="Voice Assistant",
    description="<p style='font-size:24px;text-align:center;'>Ask questions or provide commands using your voice or by typing in the textbox</p>"
)

# Play the welcome message
play_welcome_message()

# Launch the Gradio interface
interface.launch()
