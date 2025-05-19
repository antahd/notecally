#! /bin/python3

from overlaysystem import Window, screen_write, overlay_sys_init
from callogic import construct_year

def cal_ovl_init(term_size, warning=True):
    if warning == True:
        print("WARNING!!!: This is an internal library to the NoteCally project!!!")
        print("It is not recommended to be used anywhere besides with the menu system!")
        useless_var = input("Press Return to continue: ")
    global term_width
    global term_height
    global term_width_third
    global generated_years
    global control_sub_window_a
    global control_sub_window_b
    global control_sub_window_c

    term_width = (term_size.columns - 1)    # Adjustments necessary to avoid writing beyond screen buffer
    term_height = (term_size.lines - 2)     #

    term_width_third = (int(term_width / 3))

    if term_width_third < 27:
        term_width_third = 27
    elif term_width_third > 57:
        term_width_third = 74
    elif term_width_third < 58 and term_width_third > 31:
        term_width_third = 50
    else:
        term_width_third = 27

    overlay_sys_init(term_size.columns, term_size.lines)

    control_window = Window(0, 0, 0, term_width_third, (term_height - 3))
    control_window.win_draw()

    viewport_main = Window((term_width_third + 1), 0, 0, term_width, (term_height - 10))
    viewport_main.win_draw()

    statusbar = Window((term_width_third + 1), (term_height - 9), 0, term_width, (term_height - 3))
    statusbar.win_draw()

    statusbar.win_segment_cont(["Commands |"," :help/:h (Help)"," :quit/:q (Quit)", ":1-:12 (Browse calendar)"])

    footer_decor()

    generated_years = []
    
    if term_width_third >= (24 * 3): # tweak if y out of bounds
        control_sub_window_a = Window(0,1,0,26,(term_height - 3))
        control_sub_window_b = Window(24,1,0,49,(term_height - 3))
        control_sub_window_c = Window(48,1,0,(term_width_third-1), (term_height-3))
        
    if term_width_third >= (25 * 2) and term_width_third < (24 * 3): # tweak if y out of bounds
        control_sub_window_a = Window(0,0,0,25,(term_height - 3))
        control_sub_window_b = Window(24,0,0,50,(term_height - 3))

    if term_width_third < (25 * 2):
        if term_height < 30:
            control_sub_window_a = Window(0,0,0,27,(term_height - 3))
        else:
            control_sub_window_a = Window(0,0,0,27,(term_height - 3))
            
    return (control_window,viewport_main,statusbar)
            

def cal_gen_year(year, start_day_index, leap=False,debug=False):
    year = construct_year(start_day_index,leap,debug)
    generated_years.append(year)
    return generated_years

def calendar_render(year,select_month=0):
    
    if term_width_third >= (24 * 3): # tweak if y out of bounds
        
        if select_month < 4:
            select_month = 4
        elif select_month > 7:
            select_month = 7

        control_sub_window_a.win_clear()
        control_sub_window_b.win_clear()
        control_sub_window_c.win_clear()

        calparse([year[select_month - 4][0],year[select_month - 1][0],year[select_month + 2][0]],control_sub_window_a)
        calparse([year[select_month - 3][0],year[select_month][0],year[select_month + 3][0]],control_sub_window_b)
        calparse([year[select_month - 2][0],year[select_month + 1][0],year[select_month + 4][0]],control_sub_window_c)
        
        #calparse([year[0][0],year[3][0],year[6][0],year[9][0],],control_sub_window_a)  # full year
        #calparse([year[1][0],year[4][0],year[7][0],year[10][0],],control_sub_window_b) # Not a permanent solution...
        #calparse([year[2][0],year[5][0],year[8][0],year[11][0],],control_sub_window_c) #

    if term_width_third >= (25 * 2) and term_width_third < (24 * 3): # tweak if y out of bounds
        
        if select_month < 1:
            select_month = 1
        elif select_month > 9:
            select_month = 9

        control_sub_window_a.win_clear()
        control_sub_window_b.win_clear()

        calparse([year[select_month - 1][0],year[select_month+1][0]],control_sub_window_a)
    
        calparse([year[select_month][0],year[select_month+2][0]],control_sub_window_b)
    
    if term_width_third < (25 * 2):
        if select_month > 10:
            select_month = 10
        if term_height < 30:
            if select_month < 0:
                select_month = 0
            control_sub_window_a.win_clear()
            calparse([year[select_month][0],year[select_month + 1][0]],control_sub_window_a)
        else:
            if select_month < 1:
                select_month = 1
            control_sub_window_a.win_clear()
            calparse([year[select_month-1][0],year[select_month][0],year[select_month + 1][0]],control_sub_window_a)

def calparse(received_input, window):
    for input_data in received_input:
        for row in input_data:
            window.win_upd_cont(f"{row}╳", True, False, False)

def rfr_sub_win():

    try:
        control_sub_window_a.win_draw(False)
    except:
        pass
    try:
        control_sub_window_b.win_draw(False)
    except:
        pass
    try:
        control_sub_window_c.win_draw(False)
    except:
        pass
    

    footer_decor()

def footer_decor(char1="▒", char2="░"):
    i=0
    while i <= term_width:
        if i % 2:
            screen_write(i,term_height - 2, char2)
        else:
            screen_write(i, term_height - 2, char1)
        i+=1

def foot_cont(content, offset=0):
    while len(content) <= term_width:
        content = content + " "
    i=0
    for char in content:
        screen_write(i, ((term_height - 1) + offset), char)
        i+=1
