from .functions import capture,get_tvshow, select_tvshow,concatenate_segments

def run():    
    programacion= get_tvshow()
    programa= select_tvshow(programacion)
    filename= capture(programa)
    concatenate_segments(filename)