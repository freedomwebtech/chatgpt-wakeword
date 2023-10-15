import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import openai
from gtts import gTTS
import os
import pygame


# Set your Porcupine wake word and OpenAI API key
openai.api_key = 'key'

# Initialize Porcupine for wake word detection
keyword_path = "modelpath"
access_key = 'key'

# Initialize Porcupine for wake word detection
handle = pvporcupine.create(access_key=access_key, keyword_paths=[keyword_path])

# Initialize PyAudio for audio input
audio_p = pyaudio.PyAudio()

# Initialize conversation messages
messages = [{"role": "system", "content": "You are an intelligent assistant."}]

# Function to recognize speech using Google Web Speech Recognition
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio_data)
        print("You:", user_input)
        return user_input
    except sr.UnknownValueError:
        print("Sorry, I could not understand your command.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech Recognition service; {e}")
        return ""

# Function to interact with OpenAI's GPT-3
def chat_with_gpt(user_input):
    messages.append({"role": "user", "content": user_input})

    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    reply = chat.choices[0].message

    print("Assistant:", reply.content)
    speak(reply.content)

    messages.append(reply)

# Function to speak text using gTTS
def speak(audiostring):
    tts = gTTS(text=audiostring, lang="en")
    tts.save("audio.mp3")
    
    pygame.mixer.init()
    pygame.mixer.music.load("audio.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(1000)

    pygame.mixer.music.stop()  # Stop the playback
    pygame.mixer.quit()  # Quit the mixer
    os.remove("audio.mp3")
   
        
       # Main function to handle the assistant
def run_assistant():
    try:
        print("Assistant is active. Waiting for wake word...")
        pcm = audio_p.open(
            rate=handle.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=handle.frame_length,
        )

        while True:  # Continue listening indefinitely
            pcm_data = pcm.read(handle.frame_length)
            pcm_data = struct.unpack_from("h" * handle.frame_length, pcm_data)          
            keyword_index = handle.process(pcm_data)

            if keyword_index >= 0:
                print("Wake word detected. Please speak your command.")
                user_input = recognize_speech()
                if user_input:
                    if "goodbye" in user_input.lower():
                        chat_with_gpt("Goodbye!")
                        break
                    chat_with_gpt(user_input)

    except KeyboardInterrupt:
        print("Goodbye!")

if __name__ == "__main__":
    run_assistant()
