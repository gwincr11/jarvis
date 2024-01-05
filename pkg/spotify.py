import json
import webbrowser
from textwrap import dedent

import spotipy
from crewai import Task
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, tool
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
username = 'gwincr11'
redirectURI = 'http://google.com/'

auth_manager = SpotifyClientCredentials()
spotifyObject = spotipy.Spotify(auth_manager=auth_manager)
user = spotifyObject.current_user()


class SpotifyTasks():
    def findSong(self, agent, prompt):
        # results = ["items":]  # spotifyObject.current_user_saved_tracks()
        prompt = f"""
            #{prompt}

            Pick a song to play then tell me something interesting about it.
            Your final answer MUST be some information about what song you played.
        """
        print("finding song")
        # for idx, item in enumerate(results['items']):
        #    prompt += f"{idx+1}) {item['track']['name']} by {item['track']['artists'][0]['name']}\n"

        return Task(description=dedent(prompt), agent=agent)


@tool
def playSong(songName: str):
    """Play a song on spotify"""
    # Search for the Song
    searchResults = spotifyObject.search(songName, 1, 0, "track")
    # Get required data from JSON response.
    tracks_dict = searchResults['tracks']
    tracks_items = tracks_dict['items']
    song = tracks_items[0]['external_urls']['spotify']
    # Open the Song in Web Browser
    print("playing song")
    webbrowser.open(song)


if __name__ == "__main__":
    spotifyObject.current_user_top_artists()
