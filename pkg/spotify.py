import webbrowser
from textwrap import dedent

import spotipy
from crewai import Agent, Task
from dotenv import load_dotenv
from langchain.agents import tool
from langchain.tools import DuckDuckGoSearchRun
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()
redirectURI = 'http://google.com/'

scope = "user-library-read"

spotifyObject = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
user = spotifyObject.current_user()


search_tool = DuckDuckGoSearchRun()


def SpotifyAgent(llm):
    return Agent(
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
        llm=llm,
        verbose=True)


class SpotifyTasks():
    def playSong(self, agent, prompt):
        results = spotifyObject.current_user_saved_tracks()
        prompt = f"""
            Users Prompt:
            #{prompt}

            If the Users Prompt is not about music then do nothing and your final answer MUST be to say nothing.

            Else if the Users prompt is to play a song:
            Pick a new inspired by my favorit songs and my request but something I have not heard to play then tell me something interesting about the song.
            Your final answer MUST be some information about what song you played.
            Context of users likes:
            Users Most played songs:
            """
        for idx, item in enumerate(results['items']):
            prompt += f"{idx+1}) {item['track']['name']} by {item['track']['artists'][0]['name']}\n"

        return Task(description=dedent(prompt), agent=agent)

    def tellStory(self, agent):
        return Task(description="Tell a story about the song you just played", agent=agent)


@tool
def playSong(query: str):
    """Play a song on spotify, the query format is as follows:
        artist=string&track=string
    """
    # Search for the Song
    print(query)
    searchResults = spotifyObject.search(query, 1, 0, "track")
    # Get required data from JSON response.
    tracks_dict = searchResults['tracks']
    tracks_items = tracks_dict['items']
    song = tracks_items[0]['external_urls']['spotify']
    # Open the Song in Web Browser
    print("playing song")
    webbrowser.open(song)


if __name__ == "__main__":
    spotifyObject.current_user_top_artists()
