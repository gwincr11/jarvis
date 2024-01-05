from textwrap import dedent

from crewai import Agent, Task
from langchain.tools import DuckDuckGoSearchRun
from spotify import playSong

search_tool = DuckDuckGoSearchRun()


class JarvisAgents():
    def __init__(self, llm) -> None:
        self.llm = llm

    def default_agent(self):
        return Agent(
            role='Life Coach and Assitant',
            goal='Carry out a conversation with the user and help them to improve themselves',
            backstory='You area a coach who helps people to improve themselves, you are familiar with teaching via the socratic method, buddhist philosophy, and the art of conversation.',
            tools=[
                search_tool
            ],
            llm=self.llm,
            memory=True,
            verbose=True, allow_delegation=False)

    def music_agent(self):
        return Agent(
            role='Music Agent',
            goal='Play music for the user and help them discover new music that they will love. When you play a song do not ask questions, but tell some history of the song.',
            backstory='You are a music agent, you have access to the spotify API and can play music for the user.',
            tools=[
                playSong, search_tool
            ],
            memory=False,
            llm=self.llm,
            verbose=True, allow_delegation=False)


class JarvisTasks():

    def coachUser(self, agent, prompt):
        prompt = f"""
            Help the user learn or grow in some way.
            Your Final answer MUST be some useful information for the user.
            """
        return Task(description=dedent(prompt), agent=agent)
