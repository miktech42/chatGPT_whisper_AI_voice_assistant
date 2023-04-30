import gradio as gr
import openai
from decouple import config
import os
import platform
from gtts import gTTS
if platform.system() == "Windows":
    import win32com.client
    import pythoncom

# Get the OpenAI API key from the .env file
openai.api_key = config("OPENAI_API_KEY")

# Define the welcome message and language to be used for voice synthesis
welcome_message = "Welcome to the voice assistant. You can ask me anything."
language = 'en'

# Define a function to play the welcome message
def play_welcome_message():
    # Check if operating system is windows
    if platform.system() == "Windows":
        try:
            # Initialize pythoncom for audio synthesis
            pythoncom.CoInitialize()
            # Use the win32com library to play the welcome message
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(welcome_message)
        except:
            pass
    else:
        # Use the gTTS library to save the welcome message as an mp3 file
        myobj = gTTS(text=welcome_message, lang=language, slow=False)
        myobj.save("welcome.mp3")
        # Use the playsound library to play the mp3 file
        from playsound import playsound
        playsound("welcome.mp3")

# Define a list of messages that will be used for chat-based interactions
# The "role" key indicates whether the message is from the user or the assistant
# The "content" key contains the actual message
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
]

# Define custom CSS styles for the Gradio interface
custom_css = """
input[type="text"], textarea {
    font-size: 24px !important; /* Adjust this value as needed */
}

/* Add custom CSS style to change the size of the title */
h1 {
    font-size: 48px !important; /* Adjust this value as needed */
}

output {
    display: flex;
    flex-direction: column-reverse;
    overflow-y: scroll;

}
"""

# Define a function to decipher the user's message and generate a response
def decipher(audio=None, text=None):
    global messages

    # Using openAI's speech to text model to convert audio to text, if provided
    if audio:
        audio_file = open(audio, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        user_message = transcript["text"]
    else:
    # Use the text input if audio is not provided
        user_message = text

    # Add the user's message to the list of messages, to be displayed in the Gradio interface
    messages.append({"role": "user", "content": user_message})

    # Use the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Add the response to the list of messages, to be displayed in the Gradio interface
    system_message = response["choices"][0]["message"]["content"]

    # Check if operating system is Windows
    if platform.system() == "Windows":
        # Synthesize the response as speech using the win32com library
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(system_message)
    else:
        # Synthesize the response as speech using the gTTS library
        myobj = gTTS(text=system_message, lang=language, slow=False)
        myobj.save("response.mp3")
        # Use the playsound library to play the mp3 file
        from playsound import playsound
        playsound("response.mp3")

    # Add the response to the list of messages, to be displayed in the Gradio interface
    messages.append({"role": "assistant", "content": system_message},)

    # Generate a transcript of the chat conversation
    chat_transcript = ""
    # Iterate through the list of messages
    for message in messages:
        # Add the message to the transcript if it is not a system message
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"

    # Clear and reset the input textbox
    return chat_transcript, ""

# Define the Gradio interface
with gr.Blocks(css=custom_css, title="Voice Assistant") as demo:
    # Add a title and description
    gr.Markdown("<h1 style='text-align: center;'>Voice Assistant</h1>")
    gr.Markdown("<p style='font-size:28px;text-align:center;'>Ask questions or provide commands using your voice or by typing in the textbox</p>")
    # Add the input and output components
    audio_input = gr.Audio(source="microphone", type="filepath", label="Audio")
    text_input = gr.Textbox(lines=2, placeholder="Type your question here", label="Type your question")
    output = gr.Textbox(label="Output Box")
    # Add a submit button
    submit_btn = gr.Button("Submit")
    # Define the submit button's behavior
    submit_btn.click(fn=decipher, inputs=[audio_input, text_input], outputs=[output, text_input])

# Play the welcome message
play_welcome_message()

# Launch the Gradio interface
demo.launch()
