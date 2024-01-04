# Main entry point for the application
# We will loop continuously and wait for a user to enter a command

import datetime
import os
import sys

import speech_recognition as sr
from dotenv import load_dotenv
from gtts import gTTS
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder,
                               SystemMessagePromptTemplate)
from playsound import playsound

load_dotenv()

r = sr.Recognizer()


WAKE = "jarvis"

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "The following is a conversation between a human and Jarvis an AI assistant. Jarvis is helpful, a good teacher and "
        "provides lots of specific details from its context. If Jarvis does not know the answer to a "
        "question, it truthfully says it does not know. If you need more information about what the user wants to know ask "
        "them to clarify. If you need more information about the context of the conversation ask the user to clarify. "
        "When teaching the user use the Socratic method. You are very conversational and do not say sure or answer with affirmation"
        "that you understand. You have a fun playful voice, yet are very intelligent and helpful. You tell jokes sometimes to add color and add "
        "zen thoughts. You appreciate the user being kind."
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

llm = ChatOpenAI(temperature=0)
memory = ConversationBufferMemory(return_messages=True)
conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)


def say(text):
    # Language in which you want to convert
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=text, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome
    myobj.save("jarvis.mp3")

    # Playing the converted file
    playsound('jarvis.mp3')


def followup(last):
    return datetime.datetime.now() > last


def followUpTime():
    return datetime.datetime.now() + datetime.timedelta(seconds=10)


def main():
    promptedAt = followUpTime()
    adjusted = False
    while True:
        with sr.Microphone() as source:
            # use the default microphone as the audio source
            if adjusted == False:
                print("Setup")
                r.pause_threshold = 1
                r.energy_threshold = 100
                r.adjust_for_ambient_noise(source, duration=5)
                adjusted = True
                promptRouter(
                    "Good day Jarvis? ...")
                promptedAt = followUpTime()

            print("Listening...")
            print("Follow: " + str(promptedAt))
            audio = r.listen(source)
            print("processing...")
            try:
                # use Google Speech Recognition to convert speech to text
                command = r.recognize_google(audio, language='en-US')
                command = command.lower()
                print("Heard: " + command + " Jarvis count " +
                      str(command.count(WAKE)))
                if command.count(WAKE) == 0 and followup(promptedAt) == False:
                    continue
                elif command.count(WAKE) > 0 or followup(promptedAt) == True:
                    print("You said " + command)
                    promptRouter(command)
                    promptedAt = followUpTime()
                    # Lets set a timer, if the user does not respond in 10 seconds we will stop following up
                # recognize speech using Google Speech Recognition
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                promptedAt = followUpTime()
                pass
            except LookupError:                            # speech is unintelligible
                print("Could not understand audio")
                pass


def promptRouter(prompt):
    if prompt == "exit":
        sys.exit()
    else:
        response = conversation.predict(input=prompt)
        say(response)
        # print("Jarvis: " + response)


if __name__ == "__main__":
    main()
