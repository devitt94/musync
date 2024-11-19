from pydantic import BaseModel

class Song(BaseModel):
    id: str
    title: str
    artist: str
    album: str


