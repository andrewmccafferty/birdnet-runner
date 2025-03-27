import datetime

from datetime import timedelta
from requests import get
from typing import Optional

from config import LATITUDE, LONGITUDE

sunset_time_last_checked: Optional[datetime.datetime] = None

dawn_time: Optional[str] = None
dusk_time: Optional[str] = None

def set_dawn_dusk_time():
    global dawn_time
    global dusk_time
    global sunset_time_last_checked
    if sunset_time_last_checked is not None and datetime.datetime.now() - sunset_time_last_checked < timedelta(hours=24):
        return

    print("Calculating dawn dusk time from api.sunrisesunset.io...")
    response = get(f"https://api.sunrisesunset.io/json?lat={LATITUDE}&lng={LONGITUDE}&timezone=UTC&time_format=24")
    response.raise_for_status()
    response_body = response.json()
    dawn_time = response_body["results"]["dawn"]
    dusk_time = response_body["results"]["dusk"]
    print(f"Dawn time: {dawn_time}")
    print(f"Dusk time: {dusk_time}")

    sunset_time_last_checked = datetime.datetime.now()

def is_between_dusk_and_dawn():
    global dusk_time
    global dawn_time
    global sunset_time_last_checked
    set_dawn_dusk_time()

    dawn = datetime.datetime.strptime(dawn_time, "%H:%M:%S").time()
    dusk = datetime.datetime.strptime(dusk_time, "%H:%M:%S").time()
    now = datetime.datetime.now().time()
    between_dusk_and_dawn = now >= dusk or now < dawn
    if not between_dusk_and_dawn:
        print(f"It is not night time. Dusk is at {dusk_time}, dawn is at {dawn_time}")
    return between_dusk_and_dawn