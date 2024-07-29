import datetime
import decimal
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class BirdObservation(BaseModel):
    id: Optional[str] = None
    common_species_name: str
    scientific_name: str
    time: datetime.datetime
    recording_filename: str
    confidence: Decimal


class SightingReport(BaseModel):
    species_name: str
    last_hearing: datetime.datetime
    last_hearing_filename: str