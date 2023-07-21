from pydantic import BaseModel

from worker import TrackingFile


class Config(BaseModel):
    tracking_files: list[TrackingFile]
