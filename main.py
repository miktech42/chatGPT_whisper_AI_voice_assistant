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

# Custom CSS string
custom_css = """
input[type="text"], textarea {
    font-size: 20px !important; /* Adjust this value as needed */
}

/* Add custom CSS style to change the size of the title */
h1 {
    font-size: 40px !important; /* Adjust this value as needed */
}

output {
    display: flex;
    flex-direction: column-reverse;
    overflow-y: scroll;
}
"""

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

# Reset the value of the text_input component

    return chat_transcript, ""

with gr.Blocks(css=custom_css, title="Voice Assistant") as demo:
    gr.Markdown("<h1 style='text-align: center;'>Voice Assistant</h1>")
    gr.Markdown("<p style='font-size:28px;text-align:center;'>Ask questions or provide commands using your voice or by typing in the textbox</p>")
    audio_input = gr.Audio(source="microphone", type="filepath", label="Audio")
    text_input = gr.Textbox(lines=2, placeholder="Type your question here", label="Type your question")
    output = gr.Textbox(label="Output Box")
    submit_btn = gr.Button("Submit")
    submit_btn.click(fn=decipher, inputs=[audio_input, text_input], outputs=[output, text_input])

# Play the welcome message
play_welcome_message()

# Launch the Gradio interface
demo.launch()
