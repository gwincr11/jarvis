from textwrap import dedent

from crewai import Agent, Task
from langchain.agents import tool
from langchain.tools import DuckDuckGoSearchRun
from spotify import SpotifyTasks, playSong

search_tool = DuckDuckGoSearchRun()


@tool
def checkAvailableAgents():
    """Check the available agents"""
    return "{default_agent, music_agent"


class JarvisAgents():
    def __init__(self, llm) -> None:
        self.llm = llm

    def build(self, agent, prompt):
        if agent == "default_agent":
            return self.default_agent(prompt)
        elif agent == "music_agent":
            return self.music_agent(prompt)

    def pickAgent(self):
        return Agent(
            role="Your an intermediary agent that chooses the best agent for the user based on their prompt",
            goal="""
                You are an intermediary agent that chooses the best agent for the user based on their prompt,
                the availble agents are: music_agent and default_agent. Your final answer must be to choose one of these agents which
                will then be used as a python argument.
                """,
            backstory="You are an intermediary agent that chooses the best agent for the user based on their prompt",
            llm=self.llm,
            memory=True,
            verbose=True,
            allow_delegation=False
        )

    def default_agent(self, prompt):
        agent = Agent(
            role='Life Coach and Assitant',
            goal='You are the Default agent in a Chatbot. Carry out a conversation with the user and help them to improve themselves',
            backstory='You area a coach who helps people to improve themselves, you are familiar with teaching via the socratic method, buddhist philosophy, and the art of conversation.',
            tools=[
                search_tool
            ],
            llm=self.llm,
            memory=True,
            verbose=True)

        tasks = JarvisTasks()

        return agent, [tasks.coachUser(agent=agent, prompt=prompt)]

    def music_agent(self, prompt):
        agent = Agent(
            role='Music Agent',
            goal="""
            Play music for the user and help them discover new music that they will love.
            When you play a song do not ask questions, but tell some history of the song.
            """,
            backstory='You are a music agent, you have access to the spotify API and can play music for the user.',
            tools=[
                playSong, search_tool
            ],
            memory=False,
            llm=self.llm,
            verbose=True)
        music_tasks = SpotifyTasks()

        return agent, [music_tasks.playSong(agent=agent, prompt=prompt)]


class JarvisTasks():

    def coachUser(self, agent, prompt):
        newPrompt = f"""
        Respond to the following prompt: {prompt}
        Your final answer MUST be relevant to the prompt, and cite any references.
        """
        return Task(description=dedent(prompt), agent=agent)
