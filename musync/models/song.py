from pydantic import BaseModel


class Song(BaseModel):
    id: str
    title: str
    artist: str
    album: str | None = None

    def __str__(self) -> str:
        return f"{self.title} - {self.artist}"
