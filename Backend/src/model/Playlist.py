import json
from dataclasses import dataclass

import src.services.song_services.song_service_aws_lambda as song_service_aws_lambda


@dataclass
class Playlist:
    name: str
    photo: str
    description: str
    upload_date: str
    owner: str
    songs: list

    def add_songs(self, song_names: str) -> None:
        [
            self.songs.append(song_service_aws_lambda.get_song(song_name))
            for song_name in song_names
        ]

    def get_json(self) -> str:
        playlist_dict = self.__dict__

        songs_json = []

        for song in self.songs:
            song_json = song.get_json()
            songs_json.append(song_json)

        # Eliminar el atributo song_names del diccionario ,
        # hay que serializar song primero
        playlist_dict.pop("songs", None)
        # Convertir el diccionario en una cadena JSON
        playlist_dict["songs"] = songs_json
        playlist_json = json.dumps(playlist_dict)

        return playlist_json
