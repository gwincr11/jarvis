import json
import webbrowser
from textwrap import dedent

import spotipy
from crewai import Task
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, tool
from langchain.pydantic_v1 import BaseModel, Field
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

load_dotenv()
username = 'gwincr11'
redirectURI = 'http://google.com/'

scope = "user-library-read"

spotifyObject = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
user = spotifyObject.current_user()


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
        prompt += """The tool playSong must take a query parameter which is a string in the following format, replace with the correct information:

            artist=REPLACE_WITH_ARTIST_NAME&track=REPLACE_WITH_TRACK_NAME

        We must call it with both a track and an artist, neither can be null.
        The tool will then search for the song and play it in the users browser.
        Once that is done, complete a search about the song or artist.

        The final step is to tell the user something interesting about the song.
        """
        return Task(description=dedent(prompt), agent=agent)


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
