from dataclasses import dataclass
from typing import Optional


@dataclass
class SceneResult:
    description: str
    energy: int          # 1–10
    sentiment: str       # study | chill | calm | party | intense | romantic


@dataclass
class Track:
    name: str
    artist: str
    uri: str             # spotify:track:<id>
    preview_url: Optional[str]
    spotify_url: str


@dataclass
class CrowdAnalyzeResponse:
    changed: bool
    energy: int
    description: str
    sentiment: Optional[str] = None
    track: Optional[Track] = None
