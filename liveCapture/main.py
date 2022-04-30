from .functions import capture, select_tvshow,concatenate_segments,get_schedule_day

def run():    
    schedule_day= get_schedule_day()
    tvshow= select_tvshow(schedule_day)
    folder = capture(tvshow)
    concatenate_segments(folder)