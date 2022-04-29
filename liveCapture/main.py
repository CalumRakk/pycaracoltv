from functions import capture,get_programacion, select_program,concatenate_segments

def run():
    programacion= get_programacion()
    programa= select_program(programacion)
    filename= capture(programa)
    concatenate_segments(filename)