# Main entry point for the application
# We will loop continuously and wait for a user to enter a command
import datetime
import os
import sys

import speech_recognition as sr
from agents.jarvis_agents import JarvisAgents, JarvisTasks
from crewai import Crew
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
from spotify import SpotifyTasks

load_dotenv()


WAKE = "jarvis"

llm = ChatOpenAI(temperature=0)


r = sr.Recognizer()


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


def speechToText(r, audio):
    promptedAt = followUpTime()
    print("processing...")
    try:
        # use Google Speech Recognition to convert speech to text
        command = r.recognize_google(audio, language="en-US")
        # tokenize
        command = command.lower()
        print("Heard: " + command + " Jarvis count " +
              str(command.count(WAKE)))
        if command.count(WAKE) == 0 and followup(promptedAt) == False:
            return
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


class Jarvis():
    def __init__(self, prompt):
        self.prompt = prompt

    def run(self):
        agents = JarvisAgents(llm=llm)
        agents.llm = llm
        agents.memory = True
        tasks = JarvisTasks()
        music_tasks = SpotifyTasks()

        default_agent = agents.default_agent()
        music_agent = agents.music_agent()

        music_task = music_tasks.findSong(music_agent, self.prompt)
        coach_task = tasks.coachUser(default_agent, self.prompt)

        crew = Crew(
            agents=[
                default_agent, music_agent
            ],
            tasks=[music_task, coach_task],
            verbose=True
        )

        result = crew.kickoff()
        return result


def followup(last):
    return datetime.datetime.now() > last


def followUpTime():
    return datetime.datetime.now() + datetime.timedelta(seconds=10)


def main():
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.dynamic_energy_threshold = True
        r.energy_threshold = 100
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
    print("Listening...")
    stop_listening = r.listen_in_background(
        m, speechToText, phrase_time_limit=5)
    say("Good morning how can I help you? ")
    while True:
        pass


def promptRouter(prompt):
    if prompt == "exit":
        sys.exit()
    else:
        jarvis = Jarvis(prompt=prompt)
        response = jarvis.run()
        say(response)


if __name__ == "__main__":
    main()
