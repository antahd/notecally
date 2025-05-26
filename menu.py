#! /bin/python3

import os # make optional, add a configuration system to generate a first time config potentially with user interaction
from overlaysystem import screen_dbg_tape, screen_print, Window, screen_clear
from binhandler import binary_sys_init
from cal_ovl_lib import footer_decor, foot_cont, cal_ovl_init, calendar_render, cal_gen_year, rfr_sub_win

usr_sqlite = input("Enable Sqlite? (y/N)   $: ")

if usr_sqlite.upper() == "Y" or usr_sqlite.upper() == "YES":
    sqlite_enabled = True
else:
    sqlite_enabled = False

if sqlite_enabled == False:
    from cal_bin_lib import note_db_scan, read_note, write_note, file_len
else:
    #from database_actions import initialize_database
    from sqlite_gluecode import compgl_nt_index_refresh, initialize_sqlite, compgl_write_note as write_note, compgl_read_note as read_note
    initialize_sqlite()

def current_system_date():
    from datetime import datetime
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    current_date = f" Current date:  {year}-{month}-{day}"
    return current_date

try:
    current_year = current_system_date()
except:
    current_year = False


term_size = os.get_terminal_size()

cal_windowing = cal_ovl_init(term_size, current_year, False) # Warning set to false
control_window = cal_windowing[0]
viewport_main = cal_windowing[1]
statusbar = cal_windowing[2]
datebar = cal_windowing[3]

binary_sys_init(False,0,False)

def nt_index_refresh():
    notelisting = []
    dep_on = []
    dep_of = []
    try:
        notedb = note_db_scan()
        #print(notedb)
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
    return notelisting

def menushell_sys_init():

    cal_gen_year(2,False) # 2025 # rework this to a more sane approach where year switching causes year generation
    cal_gen_year(3,False) # 2026
    cal_gen_year(4,False) # 2027
    cal_gen_year(5,True) # 2028
    cal_gen_year(0,False) # 2029
    cal_gen_year(1,False) # 2030
    cal_gen_year(2,False) # 2031

    global generated_years
    generated_years = cal_gen_year(3,True) # 2032

    dep_on = []
    dep_of = []
    global notelisting
    notelisting = []
    if sqlite_enabled == False:
        notelisting = nt_index_refresh()
    else: # try except here with a reference implementation of database initialization from Joonas' code incase database is nonexistant
        notelisting = compgl_nt_index_refresh()
    #print(notelisting)

menushell_sys_init()

def cal_shell():
    yr_assumption = 0
    if datebar != False:
        datebar.win_raw_cont(current_year,True,False)
        datebar.win_draw()
    screen_print()
    def ui_rfr():
    
        control_window.win_draw()
        viewport_main.win_draw()
        statusbar.win_draw()
        if datebar != False:
            datebar.win_raw_cont(current_year,True,False)
            datebar.win_draw()

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
            if sqlite_enabled == False:
                notelisting = nt_index_refresh()
            else:
                notelisting = compgl_nt_index_refresh()
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
                    yr_assumption = 0
                else:
                    calendar_render(generated_years[yr_assumption], 0)
                    statusbar.win_clear()
                    statusbar.win_raw_cont(f"Year switched to: {usr}")

        elif usr == ":nr":
            screen_print()
            ntread = input("Note to read   $: ")
            if sqlite_enabled == False:
                ntread = ntread.replace(" ","_") + ".bin"
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
            histbool = True
            undo_rev_count = 5
            usr_clr = input("Clear viewport? Y/n   $: ")
            if usr_clr.upper() != "N" and usr_clr.upper() != "NO":
                viewport_main.win_clear()
            while writing == True:
                if error_state == False:
                    statusbar.win_clear()
                    statusbar.win_segment_cont(["",":X Cancel", ":d Done/Save.",":clr Clear",":ud Undo",":rev Undo history", "count" ,":hist Disable/Enable","Undo history", "| Special edit", " commands:","/u /d", "/l /r for", "Up, Down,", "Left, Right","| :T","<amount>","<char>","Repeat <char>"])
                screen_print()
                error_state = False
                usr = input("Write to note   $: ")
                if usr == ":h":
                    error_state = True # this is to avoid printing the same help instructions again, wasting resources
                    statusbar.win_clear()
                    statusbar.win_segment_cont(["",":X Cancel", ":d Done/Save.",":clr Clear",":ud Undo",":rev Undo history", "count" ,":hist Disable/Enable","Undo history", "| Special edit", " commands:","/u /d", "/l /r for", "Up, Down,", "Left, Right","| :T","<amount>","<char>","Repeat <char>"])
               
                if usr == ":clr":
                    viewport_main.win_clear()
                if usr == ":rev":
                    usr_rev = input("Revision history count   $: ")
                    try:
                        undo_rev_count = int(usr_rev)
                        error_state = True
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Historical","revision","limit","set to",f"{str(undo_rev_count)}"])
                    except:
                        error_state = True
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Invalid user input."])

                elif usr == ":hist":
                    if histbool == False:
                        histbool = True
                        error_state = True
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Content","revision","history","enabled.",])
                    else:
                        histbool = False
                        error_state = True
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","WARNING: ","Content","revision","history","saving","disabled!","Further","edits","will","not","save","to","RAM!",])

                elif usr == ":ud":
                    rev_exist = len(viewport_main.content_history)
                    if rev_exist > 0:
                        try:
                            undo_val = input(f"How far to undo? {str(rev_exist - 1)} previous entries exist.   $: ")
                            undo_val = (rev_exist - 1) - int(undo_val)
                            #print(undo_val)
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

                elif len(usr) > 1 and usr[0] == ":" and usr[1] == "T":
                    try:
                        if usr[2] == " ":
                            command = usr.split(" ")
                            #print(command)
                            factor = command[1]
                            #print(factor)
                            variable = command[2]
                            #print(variable)
                            output = ""
                            for _ in range(0, int(factor)):
                                output += variable
                            output = output.replace("/u","┼")
                            output = output.replace("/d","╳")
                            output = output.replace("/r","╲")
                            output = output.replace("/l","╱")
                            if histbool == True:
                                while len(viewport_main.content_history) > undo_rev_count:
                                    viewport_main.content_history.pop(0)
                            viewport_main.win_upd_cont(output, True, True, histbool)
                    except:
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Error!", " usage :T <int> <symbols","to repeat>", "",""])
                        error_state = True

                elif len(usr) > 0 and usr[0] != ":":
                    usr = usr.replace("/u","┼")
                    usr = usr.replace("/d","╳")
                    usr = usr.replace("/r","╲")
                    usr = usr.replace("/l","╱")

                    if histbool == True and len(viewport_main.content_history) > undo_rev_count:
                        viewport_main.content_history.pop(0)
                    viewport_main.win_upd_cont(usr, True, True, histbool)
                
                elif usr == ":X":
                    writing = False
                    viewport_main.win_histclr()
                    statusbar.win_clear()
                    statusbar.win_segment_cont(["Commands |"," :help/:h (Help)"," :quit/:q (Quit)", ":1-:12 (Browse calendar)"])
                    suppress_last = True
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
                        if sqlite_enabled == False:
                            uuid = input("ID   $:")
                        else:
                            uuid = 0
                        name = input("Title/Name   $: ")
                        write_note(tuple(date), int(uuid), name, viewport_main.last_content)
                        writing = False
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Note written as:", f"{name}"])
                        viewport_main.win_histclr()
                        if sqlite_enabled == False:
                            notelisting = nt_index_refresh()
                        else:
                            notelisting = compgl_nt_index_refresh()
                    except:
                        statusbar.win_clear()
                        statusbar.win_segment_cont(["","Error during", "save process.", "Please try", "again and", "follow the", "prompt instructions", "closely."])
                        error_state = True

        elif usr == ":nl":
            if sqlite_enabled == False:
                notelisting = nt_index_refresh()
            else:
                notelisting = compgl_nt_index_refresh()
            #print(notelisting)
            viewport_main.win_clear()
            viewport_size = viewport_main.win_ret_relat_pos()
            columns = (viewport_size[1][1] - viewport_size[0][1]) - 2
            #print(viewport_size)
            #print(columns)
            offset = 0
            if offset+columns < len(notelisting):
                while offset+columns <= len(notelisting):
                    viewport_main.win_clear()
                    viewport_main.win_upd_cont("   ID   |   Title   |   Date ╳")
                    
                    for i in range(0, columns):
                        disp_id = notelisting[i+offset][0]
                        disp_title = notelisting[i+offset][1]
                        ML = notelisting[i+offset][2][0]
                        YYY = notelisting[i+offset][2][1]
                        MN = notelisting[i+offset][2][2]
                        DT = notelisting[i+offset][2][3]
                        year = ((ML*1000)+YYY)
                        disp_date = str(year) + "." + str(MN) + "." + str(DT)
                        viewport_main.win_upd_cont(f"   {disp_id} - {disp_title} - {disp_date} ╳")

                    screen_print()
                    usr = input(f"Browse 0-{str(len(notelisting)-columns)} / Current: {str(offset)}   $: ")
                    
                    try:
                        int(usr)
                    except:
                        pass
                    else:
                        if int(usr) <= (len(notelisting) - columns):
                            offset = int(usr)
                        else:
                            offset = len(notelisting) - columns

                    if usr == "":
                        offset += 1
                    elif usr == "q" or usr == "Q" or usr == ":q":
                        break
            else:
                viewport_main.win_upd_cont("   ID   |   Title   |   Date ╳")
                for item in notelisting:
                    disp_id = item[0]
                    disp_title = item[1]
                    ML = item[2][0]
                    YYY = item[2][1]
                    MN = item[2][2]
                    DT = item[2][3]
                    year = ((ML*1000)+YYY)
                    disp_date = str(year) + "." + str(MN) + "." + str(DT)
                    viewport_main.win_upd_cont(f"   {disp_id} - {disp_title} - {disp_date} ╳")

        elif usr == ":tp":
            screen_dbg_tape()
        elif usr == ":rfr":
            statusbar.win_clear()
            statusbar.win_segment_cont(["Commands |"," :help/:h (Help)"," :quit/:q (Quit)", ":1-:12 (Browse calendar)"])
            foot_cont("")
            suppress_last = True
            ui_rfr()
        elif usr == ":q" or usr == ":quit":
            break
        elif len(usr) > 1 and usr[0] == ":":

            try:
                usr_int = int(usr.strip(":"))
                if sqlite_enabled == False:
                    notelisting = nt_index_refresh()
                else:
                    notelisting = compgl_nt_index_refresh()
                viewport_main.win_clear()
                control_window.win_clear()
                viewport_size = viewport_main.win_ret_relat_pos()
                columns = (viewport_size[1][1] - viewport_size[0][1]) - 2
                viewport_main.win_upd_cont("   ID   |   Title   |   Date ╳")
                for item in notelisting:
                    disp_id = item[0]
                    disp_title = item[1]
                    ML = item[2][0]
                    YYY = item[2][1]
                    MN = item[2][2]
                    DT = item[2][3]
                    year = ((ML*1000)+YYY)
                    disp_date = str(year) + "." + str(MN) + "." + str(DT)
                    if year == yr_assumption + 2025 and usr_int == MN:
                        viewport_main.win_upd_cont(f"   {disp_id} - {disp_title} - {disp_date} ╳")

                if len(usr) < 3:
                    sanitized_usr = usr[1]
                else:
                    sanitized_usr = 10 + int(usr[2])
                calendar_render(generated_years[yr_assumption], (int(sanitized_usr)-1))
            except:
                statusbar.win_clear()
                statusbar.win_segment_cont(["","Unknown input.", "Try typing :h or :help"])
            
        else:
            statusbar.win_clear()
            statusbar.win_segment_cont(["","Unknown input.", "Try typing :h or :help"])
        if suppress_last == False:
            foot_cont(f"Last command issued: {usr}")
        screen_print()

cal_shell()