# Main entry point for the application
# We will loop continuously and wait for a user to enter a command
import datetime
import sys
from textwrap import dedent

import speech_recognition as sr
from agents.jarvis_agents import JarvisAgents, JarvisTasks
from crewai import Crew, Task
from dotenv import load_dotenv
from gtts import gTTS
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from playsound import playsound

load_dotenv()

WAKE = "jarvis"
llm = ChatOpenAI(temperature=0)
r = sr.Recognizer()


def say(text):
    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=text, lang="en", slow=False)
    # Saving the converted audio in a mp3 file
    myobj.save("jarvis.mp3")
    # Playing the converted file
    playsound('jarvis.mp3')


def followup(last):
    return datetime.datetime.now() > last


def followUpTime():
    return datetime.datetime.now() + datetime.timedelta(seconds=10)


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
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        pass
    except LookupError:   # speech is unintelligible
        print("Could not understand audio")
        pass


class Jarvis():
    def __init__(self, prompt):
        prompt = prompt.lower()
        prompt = prompt.replace("jarvis", "")
        self.prompt = prompt

    def run(self):
        agents = JarvisAgents(llm=llm)
        pickAgent = agents.pickAgent()
        pickPrompt = f"""
        Pick between the following agents: [default_agent, music_agent]
        The default agent is a life coach and assistant, the music agent is a music player
        The prompt which the agent will be given is: {self.prompt}

        Your answer must be one of the following: [default_agent, music_agent]
        """
        task = Task(description=dedent(pickPrompt), agent=pickAgent)

        crew = Crew(
            agents=[
                pickAgent
            ],
            tasks=[task],
            verbose=True
        )

        result = crew.kickoff()
        print(result)
        agent, tasks = agents.build(agent=result, prompt=self.prompt)
        crew = Crew(
            agents=[
                agent
            ],
            tasks=tasks,
            verbose=True
        )
        result = crew.kickoff()
        return result


def main():
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.dynamic_energy_threshold = True
        r.energy_threshold = 100
        r.pause_threshold = 10
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
