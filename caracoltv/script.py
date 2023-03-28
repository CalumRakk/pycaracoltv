
from .utils import (
    capture,
    select_tvshow,
    get_schedule_day,
    select_resolution
)

def schedule():
    schedule_day = get_schedule_day()
    tvshow = select_tvshow(schedule_day)

    qualities = [select_resolution()]
    if len(qualities) < 2:
        capture(tvshow, quality=qualities[0])
