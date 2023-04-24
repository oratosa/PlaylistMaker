import re, requests, unicodedata, os, base64
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import functions_framework
from bs4 import BeautifulSoup
from datetime import datetime


@functions_framework.cloud_event
def handler(cloud_event):
    # scraping
    pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
    print(f"Pub/Sub message is {pubsub_message}")
    print("A scraping procedure starts...")
    scraping = Scraping(url="https://www4.nhk.or.jp/sunshine/66/")
    html = scraping.html

    on_air_date = scraping.get_on_air_date(html)
    track_list = scraping.generate_track_list(html)

    print(f"The scraping result on {on_air_date} is the following...")
    [print(i) for i in track_list]

    # spotify authorization
    playlistmaker = PlaylistMaker()

    # get the track information from spotify
    uris = playlistmaker.generate_track_id_list(track_list)

    print(
        f"Track's Spotify URIs based on the scraping result on {on_air_date} are the following..."
    )
    [print(f"{i+1},{j}") for i, j in enumerate(uris)]

    # make a playlist
    available_uris = [row[0] for row in uris if row[0] != "URI is not found"]
    name = f"Weekend Sunshine by Peter Barakan {on_air_date}"
    description = (
        """NHKのラジオ番組 Weekend Sunshine で放送された楽曲をプレイリストにしています。自動的に作成しているため誤りがあるかもしれません。"""
    )

    playlist_id = playlistmaker.identify_playlist(name)
    if playlist_id is None:
        playlistmaker.make_playlist(name, description, available_uris)
        print("A new playlist was made.")
    else:  ## if the playlist is already existed, remove the tracks and readd the tracks.
        track_list = playlistmaker.get_tracks_from_playlist(playlist_id)
        playlistmaker.sp.playlist_remove_all_occurrences_of_items(
            playlist_id, track_list
        )
        playlistmaker.sp.playlist_add_items(playlist_id, available_uris)
        print("The tracks in the existing playlist were deleted and added again.")

    print("The procedure was finished.")


class Scraping:
    def __init__(self) -> None:
        self.url = None
        self.html = None
        pass

    def get_html(self, url):
        data = requests.get(url)
        soup = BeautifulSoup(data.content, "html.parser")
        return soup

    def get_on_air_date(self, html) -> datetime.date:
        text = html.get_text()
        text = unicodedata.normalize("NFKC", text)
        result = re.findall(r"[0-9]+", text)
        on_air_date = "-".join(result)
        on_air_date = datetime.strptime(on_air_date, "%Y-%m-%d").date()
        return on_air_date

    def generate_track_list(self, html) -> list:
        track_list = []
        for i, l in enumerate(html.find_all("li")):
            num = str(i + 1).zfill(2)
            text = l.text.strip()
            text = unicodedata.normalize("NFKC", text)
            track = re.sub(r"( / )|( // )", "//", text)  # （曲順. 曲名 / アーティスト名 // アルバム名）
            track = re.sub(r"'", "'", track)
            track = num + "//" + track
            track = track.split("//")
            track_list.append(track)
        return track_list


class PlaylistMaker:
    def __init__(self) -> None:
        self.client_id = os.environ.get("CLIENT_ID")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.user_id = os.environ.get("USER_ID")
        self.redirect_uri = os.environ.get("REDIRECT_URI")
        self.sp = self.authorization()
        pass

    def authorization(self):
        scope = "user-library-read playlist-modify-public"
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=".cache")
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            cache_handler=cache_handler,
            scope=scope,
        )

        sp = spotipy.Spotify(auth_manager=auth_manager)

        return sp

    def generate_track_id_list(self, scraping_result: list) -> list:
        uris = []
        for row in scraping_result:
            if len(row) == 4:
                track = row[1] if row[1] else None
                artist = row[2] if row[2] else None
                album = row[3] if row[3] else None
                uri = self.get_spotify_track_info(track, artist, album)
                uris.append(uri)
            else:
                track = row[1] if row[1] else None
                artist = row[2] if row[2] else None
                album = None
                uri = self.get_spotify_track_info(track, artist, album)
                uris.append(uri)
        return uris

    def get_spotify_track_info(self, track: str, artist: str, album: str) -> tuple:
        query = f"{track} artist:{artist}"
        results = self.sp.search(q=query, type="track", limit=50)

        if results["tracks"]["total"] != 0:
            candidate = (
                results["tracks"]["items"][0]["uri"],
                results["tracks"]["items"][0]["name"],
                results["tracks"]["items"][0]["artists"][0]["name"],
                results["tracks"]["items"][0]["album"]["name"],
            )

            for result in results["tracks"]["items"]:
                uri = result["uri"]
                track_name = result["name"]
                artist_name = result["artists"][0]["name"]
                album_name = result["album"]["name"]

                if (
                    track_name in track
                    and artist_name in artist
                    and album_name in album
                ):
                    print(
                        f"Track:{track_name}, Artist:{artist_name}, Album:{album_name} were all matched!!!"
                    )
                    candidate = (uri, track_name, artist_name, album_name)

                    break

            return candidate

        else:
            candidate = ("URI is not found", track, artist, album)
            return candidate

    def make_playlist(self, name: str, description: str, uris: list) -> str:
        playlist_name = name
        playlist_description = description

        playlist = self.sp.user_playlist_create(
            self.user_id, playlist_name, public=True, description=playlist_description
        )
        playlist_id = playlist["id"]
        self.sp.playlist_add_items(playlist_id, uris)

        return playlist_id

    def identify_playlist(self, name: str) -> str:
        playlists = self.sp.current_user_playlists(limit=50, offset=0)
        for playlist in playlists["items"]:
            if playlist["name"] == name:
                return playlist["id"]

    def get_tracks_from_playlist(self, playlist_id: str) -> list:
        tracks = self.sp.playlist(playlist_id)
        track_list = [track["track"]["id"] for track in tracks["tracks"]["items"]]
        return track_list
