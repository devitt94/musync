from musync.models import Song

from pydantic import BaseModel


class Playlist(BaseModel):
    id: str
    name: str
    songs: list[Song]

    def __str__(self) -> str:
        return f"{self.name} ({len(self.songs)} songs)"
