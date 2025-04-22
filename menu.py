#! /bin/python3

import os # make optional, add a configuration system to generate a first time config potentially with user interaction
from overlaysystem import screen_dbg_tape, overlay_sys_init, screen_print, Window, screen_clear
from callogic import construct_month, construct_year
from cal_ovl_lib import footer_decor, foot_cont, calparse, cal_ovl_init, calendar_render, cal_gen_year, cls_sub_win

term_size = os.get_terminal_size()

cal_windowing = cal_ovl_init(term_size, False) # Warning set to false
    # return (control_window,viewport_main,statusbar)
control_window = cal_windowing[0]
viewport_main = cal_windowing[1]
statusbar = cal_windowing[2]

cal_gen_year("2025",2,False,True)
cal_gen_year("2026",3,False,True)
cal_gen_year("2027",4,False,True)
cal_gen_year("2028",5,True,True)
cal_gen_year("2029",0,False,True)
cal_gen_year("2030",1,False,True)
cal_gen_year("2031",2,False,True)
generated_years = cal_gen_year("2032",3,True,True)

#def ui_cls():
    
#    control_window.win_draw()
#    viewport_main.win_draw()
#    statusbar.win_draw()

#    foot_cont(" ",1)
#    footer_decor()

#    cls_sub_win()

def cal_shell():
    screen_print()
    yr_assume = 0
    def ui_cls():
    
        control_window.win_draw()
        viewport_main.win_draw()
        statusbar.win_clear()
        statusbar.win_segment_cont(["Commands |"," :help/:h (Help)"," :quit/:q (Quit)"])
        statusbar.win_draw()

        foot_cont(" ",1)
        footer_decor()

        cls_sub_win()
    while True:
        suppress_last = False
        usr = input("$: ")

        if usr == ":h" or usr == ":help":
            statusbar.win_clear()
            statusbar.win_segment_cont(["","1-12 Cycles calendar month |", "To quit do :q |",":cls (re-print screen) |",":tp (debug tape) |", "To switch years do :y |"])
        
        if usr == ":y" or usr == ":year":
            screen_print()
            usr_yr = input("Specify Year (XXXX)   $: ")
            try:
                yr_assume = (int(usr_yr) - 2025)
                generated_years[(int(usr_yr) - 2025)]
            except:
                foot_cont(f"Invalid year: {usr_yr}")
                suppress_last = True
            usr = 0 # refreshes calendar in hacky way
        
        if usr == ":tp":
            screen_dbg_tape()

        if usr == ":cls" or usr == ":clear":
            ui_cls()

        if usr == ":q" or usr == ":quit":
            break

        try:
            int(usr)
        except:
            pass
        else:
            control_window.win_clear()
            calendar_render(generated_years[yr_assume], (int(usr)-1))
        
        if suppress_last == False:
            foot_cont(f"Last: {str(usr)}   |   Year: {str(yr_assume+2025)}")
        screen_print()

cal_shell()