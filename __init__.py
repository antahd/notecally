def conf_verify():
    with open("nt_cally.cfg", 'rt') as file:
        config_str = file.read()
        file.close()
    config_internal = config_str.split("\n")
    for item in config_internal:
        var = item.split("=")
        if var[0] == "sqlite_enabled":
            global sqlite_pass
            if var[1] == "yes":
                sqlite_pass = True
            elif var[1] == "ask":
                sqlite_pass = True
            elif var[1] == "no":
                sqlite_pass = True
        elif var[0] == "user_interface":
            global ui_pass
            global ui_choice
            if var[1] == "graphical":
                ui_pass = True
                ui_choice = 1
            if var[1] == "terminal":
                ui_pass = True
                ui_choice = 0
        elif var[0] == "height":
            global height_pass
            global term_height
            if int(var[1]) > 19:
                height_pass = True
                term_height = int(var[1])
        elif var[0] == "width":
            global size_pass
            global term_width
            if int(var[1]) > 69 and height_pass == True:
                size_pass = True
                term_width = int(var[1])

ui_pass = False
sqlite_pass = False
height_pass = False
size_pass = False

try:
    conf_verify()
except:
    print("Configuration was not read succesfully.")
else:
    conf_verify()

if size_pass == False or sqlite_pass == False or ui_pass == False:
    print("No valid configuration detected. \n \n You will now go through the configuration Wizard,\n in order to generate a valid configuration.")
    os_import_error = False
    try:
        import os
    except:
        os_import_error = True
        term_width = 80
        term_height = 24
    else:
        term_width = os.get_terminal_size().columns
        term_height = os.get_terminal_size().lines

    while sqlite_pass == False:
        print("Do you wish to use SQLite as your backend?")
        usr_sql = input("Use SQLite with NoteCally? Y/N/A(Always Ask): ")
        if usr_sql.upper() == "Y":
            sqlite_choice = "yes"
            break
        elif usr_sql.upper() == "N":
            sqlite_choice = "no"
            break
        elif usr_sql.upper() == "A":
            sqlite_choice = "ask"
            break

    while ui_pass == False:
        print("Do you wish to use the terminal as your interface?")
        gui_vs_tui = input("Or use a graphical window to interact with NoteCally? T/G: ")
        if gui_vs_tui.upper() == "G":
            ui_choice = 1
            break
        elif gui_vs_tui.upper() == "T":
            ui_choice = 0
            break

    while size_pass == False and ui_choice == 0:
        screen_calibration = ""
        i=0
        while i < term_width:
            screen_calibration += "#"
            i+=1
        print(screen_calibration)
        print("This hashtag/numbersign row should NOT overflow to the next row\nIf it does please reply with N.\nYou should also reply with N if the hashtags do not reach the screen edge.")
        usr_agree = input("Is the screen width calibration correct with no overflow? y/N: ")
        if usr_agree.upper() == "Y" or usr_agree.upper() == "YES":
            break
        else:
            usr_width = input("Specify screen width: ")
            try:
                usr_width = int(usr_width)
            except:
                pass
            else:
                term_width = usr_width

    infotext = ("This hashtag/nubmersign row should be", "the exact height of your terminal/screen.", "To help with distinguishing the start and end,", "the start is marked with A, the end with B" )
    while size_pass == False and ui_choice == 0:

        i=0
            
        while i < term_height - 1:
            if i < 1:
                print(f"A {infotext[i]}")
            elif i >= 1 and i <= 3:
                print(f"# {infotext[i]}")
            else:
                print("#")
            i+=1
        usr_agree = input("B   Is the screen height correct (Do you see A and B)? y/N: ")
        if usr_agree.upper() == "Y" or usr_agree.upper() == "YES":
            break
        else:
            usr_height = input("Specify screen height: ")
            try:
                usr_height = int(usr_height)
            except:
                pass
            else:
                term_height = usr_height

    if ui_choice == 1:
        ui_choice_cfg = "graphical"
    else:
        ui_choice_cfg = "terminal"

    config_text= f"""user_interface={ui_choice_cfg}
sqlite_enabled={sqlite_choice}
width={term_width}
height={term_height}"""
    
    with open("nt_cally.cfg", 'wt') as file:
        file.write(config_text)
        file.close()

if ui_choice == 1:
    import layout
else:
    import menu