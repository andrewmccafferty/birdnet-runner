import datetime
from typing import Optional

from pydantic import BaseModel


class BirdObservation(BaseModel):
    id: Optional[str] = None
    common_species_name: str
    scientific_name: str
    time: datetime.datetime
    recording_filename: str