#! /bin/python3

import os # make optional, add a configuration system to generate a first time config potentially with user interaction
from overlaysystem import screen_dbg_tape, screen_print, Window, screen_clear
from binhandler import binary_sys_init
from cal_ovl_lib import footer_decor, foot_cont, cal_ovl_init, calendar_render, cal_gen_year, rfr_sub_win
from cal_bin_lib import note_db_scan, read_note, write_note, file_len

term_size = os.get_terminal_size()

cal_windowing = cal_ovl_init(term_size, False) # Warning set to false
control_window = cal_windowing[0]
viewport_main = cal_windowing[1]
statusbar = cal_windowing[2]

binary_sys_init(False,0,False)

def menushell_sys_init():

    cal_gen_year("2025",2,False) # rework this to a more sane approach where year switching causes year generation
    cal_gen_year("2026",3,False)
    cal_gen_year("2027",4,False)
    cal_gen_year("2028",5,True)
    cal_gen_year("2029",0,False)
    cal_gen_year("2030",1,False)
    cal_gen_year("2031",2,False)

    global generated_years
    generated_years = cal_gen_year("2032",3,True)

    dep_on = []
    dep_of = []

    notelisting = []
    note = []

    try:
        global notedb
        notedb = note_db_scan()
        i=0
        while i < len(notedb[0]):
            if notedb[0][i] == "UUID":
                uuid = notedb[0][i+1]

            if notedb[0][i] == "TITLE":
                title = notedb[0][i+1]

            if notedb[0][i] == "DEP ON":
                dep_on.append(notedb[0][i+1])

            if notedb[0][i] == "DEP OF":
                dep_of.append(notedb[0][i+1])

            if notedb[0][i] == "YEAR":
                year = notedb[0][i+1]

            if notedb[0][i] == "BRK":
                notelisting.append((uuid,title,year,dep_on,dep_of))
                uuid = 0
            i+=1
    except:
        file = open("nt_index.dat", 'wb')
        file.close()
        
    print(notelisting)

menushell_sys_init()

def cal_shell():
    screen_print()
    yr_assumption = 0
    def ui_rfr():
    
        control_window.win_draw()
        viewport_main.win_draw()
        statusbar.win_draw()

        foot_cont(" ",1)
        footer_decor()

        rfr_sub_win()

    while True:
        suppress_last = False
        usr = input("$: ")

        if usr == ":h" or usr == ":help":
            statusbar.win_clear()
            statusbar.win_segment_cont(["",":1-:12 Cycles calendar month |", "To quit do :q |",":rfr (re-print screen) |",":tp (debug tape) |", "To switch years do :y |",":nr Read note |",":nw Note write |",":clr Clear entire screen"])        
        elif usr == ":y" or usr == ":year":
            foot_cont(f"Last command issued: {usr}")
            screen_print()
            usr = input("Specify Year (XXXX)   $: ")
            suppress_last = True
            try:
                yr_assumption = (int(usr) - 2025)
            except:
                statusbar.win_clear()
                statusbar.win_segment_cont(["","Unknown year input.", "Try specifying an integer."])
            else:
                if yr_assumption >= len(generated_years) or yr_assumption < 0:
                    statusbar.win_clear()
                    statusbar.win_segment_cont(["","Year selection out of bounds.", f"Try a year between 2025 and 2032"])
                else:
                    calendar_render(generated_years[yr_assumption], 0)
                    statusbar.win_clear()
                    statusbar.win_raw_cont(f"Year switched to: {usr}")

        elif usr == ":nr":
            screen_print()
            ntread = input("Note to read   $: ")
            try:
                note = read_note(ntread, True)
                viewport_main.win_clear()
                viewport_main.win_raw_cont(note[1])
                statusbar.win_clear()
                statusbar.win_raw_cont(f"ID: {note[2]}   Title: {note[5]}╳Date: {str(note[0][0])}.{str(note[0][1])}.{str(note[0][2])}")
            except:
                statusbar.win_clear()
                statusbar.win_segment_cont(["","Error:", "Invalid note name or other exception"])
        elif usr == ":clr":
            statusbar.win_clear()
            statusbar.win_segment_cont(["Commands |"," :help/:h (Help)"," :quit/:q (Quit)", ":1-:12 (Browse calendar)"])
            viewport_main.win_clear()
            control_window.win_clear()
            
        elif usr == ":nw":
            writing = True
            error_state = False
            histbool = False
            while writing == True:
                if error_state == False:
                    statusbar.win_clear()
                    statusbar.win_segment_cont(["",":X Cancel", ":d Done/Save.",":clr Clear", "| Special", " commands:","/u /d", "/l /r for", "Up, Down,", "Left, Right","| :T","<amount>","<char>","Repeat <char>"])
                screen_print()
                error_state = False
                usr = input("Write to note   $: ")
                if usr == ":clr":
                    viewport_main.win_clear()
                elif usr == ":hist":
                    if histbool == False:
                        histbool = True
                    else:
                        histbool = False

                elif usr == ":ud":
                    rev_exist = len(viewport_main.content_history)
                    if rev_exist > 0:
                        try:
                            undo_val = input(f"How far to undo? {rev_exist} previous entries exist.   $: ")
                            undo_val = (rev_exist - 1) - int(undo_val)
                            print(undo_val)
                            print(viewport_main.content_history)
                            print(viewport_main.content_history[undo_val])
                            sel_revision = viewport_main.content_history[undo_val]
                            viewport_main.win_clear()
                            viewport_main.win_raw_cont(sel_revision)
                        except:
                            statusbar.win_clear()
                            statusbar.win_segment_cont(["","Error:", "Invalid user", "input.",""])
                            error_state = True
                    else:
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Error:", "Content history", "doesn't","exist!"])
                        error_state = True

                elif len(usr) > 0 and usr[0] == ":" and usr[1] == "T":
                    try:
                        if usr[2] == " ":
                            command = usr.split(" ")
                            print(command)
                            factor = command[1]
                            print(factor)
                            variable = command[2]
                            print(variable)
                            output = ""
                            for _ in range(0, int(factor)):
                                output += variable
                            output = output.replace("/u","┼")
                            output = output.replace("/d","╳")
                            output = output.replace("/r","╲")
                            output = output.replace("/l","╱")
                            if histbool == True and len(viewport_main.content_history) > 7:
                                viewport_main.content_history.pop(0)
                            viewport_main.win_upd_cont(output, True, True, histbool)
                    except:
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Error!", " usage :T <int> <symbols","to repeat>", "",""])
                        error_state = True

                elif usr != ":X" and usr != ":d" and len(usr) > 0:
                    usr = usr.replace("/u","┼")
                    usr = usr.replace("/d","╳")
                    usr = usr.replace("/r","╲")
                    usr = usr.replace("/l","╱")

                    if histbool == True and len(viewport_main.content_history) > 7:
                        viewport_main.content_history.pop(0)
                    viewport_main.win_upd_cont(usr, True, True, histbool)
                
                elif usr == ":X":
                    writing = False
                elif usr == ":d":
                    date = []
                    statusbar.win_clear()
                    statusbar.win_segment_cont(["","For the year 2025; Millenium = 2,", "last hundred years = 25"])
                    screen_print()
                    try:
                        millenium = input("Millenium (0-255)   $: ")
                        date.append(int(millenium))
                        hundreds = input("Last hundred years (0-999)   $: ")
                        hundreds = int(hundreds)
                        while hundreds > 255:
                            date.append(255)
                            hundreds-=255
                        if hundreds <= 255 and hundreds > 0:
                            date.append(hundreds)
                        while len(date) < 5:
                            date.append(0)
                        month = input("Month (1-12)   $: ")
                        date.append(int(month))
                        day = input("Day   $:")
                        date.append(int(day))
                        #print(date)
                        uuid = input("ID   $:")
                        name = input("Title/Name   $: ")
                        write_note(tuple(date), int(uuid), name, viewport_main.last_content)
                        writing = False
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Note written as:", f"{name}"])
                    except:
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Error during", "save process.", "Please try", "again and", "follow the", "prompt instructions", "closely."])
                        error_state = True

        elif usr == ":nl":
            pass


        elif usr == ":tp":
            screen_dbg_tape()
        elif usr == ":rfr":
            statusbar.win_clear()
            statusbar.win_segment_cont(["Commands |"," :help/:h (Help)"," :quit/:q (Quit)", ":1-:12 (Browse calendar)"])
            ui_rfr()
        elif usr == ":q" or usr == ":quit":
            break
        elif usr[0] == ":":
            try:
                int(usr[1])
            except:
                statusbar.win_clear()
                statusbar.win_segment_cont(["","Unknown input.", "Try typing :h or :help"])
            else:
                control_window.win_clear()
                if len(usr) < 3:
                    sanitized_usr = usr[1]
                else:
                    sanitized_usr = 10 + int(usr[2])
                calendar_render(generated_years[yr_assumption], (int(sanitized_usr)-1))
        else:
            statusbar.win_clear()
            statusbar.win_segment_cont(["","Unknown input.", "Try typing :h or :help"])
        if suppress_last == False:
            foot_cont(f"Last command issued: {usr}")
        screen_print()

cal_shell()