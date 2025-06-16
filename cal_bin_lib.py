#! /bin/python3

"""
Calendar binary handler.

This file contains non-generic functions used speficically
for handling binary operations within NoteCally
"""

from binhandler import bin_encode, bin_decode, bin_write, bin_read, binary_sys_init, bin_read_precise

hbc = 32 # header byte count

#binary_sys_init(False,0,False)

def header_gen(id_input, name_input, date_input): # tuple; first index contains only own uuid, second index contains potential dependencies, third index contains items which depend on self
    """
    header_gen() A sub function that generates header via another sub function: id_gen().

    Required params:
        - id_input; a tuple typically generated while using write_note(),
          aka id_tuple in write_note()

        - name_input; a tuple with decimal values used for specially encoded text

        - date_input; a tuple with 7 decimal values,
          an example for the date 2999.2.28: (2,255,255,255,234,2,28)
          1st byte: millenium, 2nd to 5th byte are combined for years 1-999
          6th byte: month, 7th byte: day
        
    Returns:
        - a tuple, binary header which containst metadata for notes/calendar markings.
    
    """
    header_self = id_gen("SELF",id_input[0])
    header_dep_on = ()
    header_dep_of = ()
    if len(id_input) > 1: # if id_input, the id tuple has more than one entry, so 2 or 3:
        for item in id_input[1]: # for each item in id_input' second index:
            header_dep_on += id_gen("DEPENDS_ON",item) # with the sub function id_gen, add the current item to header_dep_on
    if len(id_input) == 3: # if id_input has a third entry, a tuple of dependants upon self information:
        for item in id_input[2]: # for each item in id_input' third index:
            header_dep_of += id_gen("DEPENDANT_OF",item) # with the sub function id_gen, add the current item to header_dep_of
    
    return header_self + header_dep_on + header_dep_of + name_input + (50,51) + date_input + (30,31)

def id_gen(id_type,uuid,debug=False):
    """
    id_gen() A sub function, for a sub function. Generates and
    returns binary tag for ID + actual ID input as uuid.

    Required params:
        - id_type; str, accepted values: "SELF",DEPENDS_ON","DEPENDANT_OF"
        - uuid; int, any ID 0 to max of: (with an hbc, header byte count of 32, 32*255=8160)

    Optional params:
        - debug; toggles debug on or off, prints how uuid
          is broken up into binary compatible decimal values

    Returns:
        - a tuple, either the notes own ID, a dependancy or
          dependant with apropriate binary value tag at beginning
    """
    bin_buffer = []

    if uuid > (255*hbc):
        raise ValueError(f"Given UUID is too large. Maximum value: (hbc * 255 -> {hbc*255}) NOT {uuid}")

    if id_type == "SELF":
        id_tuple = (10,11) #binary 10 and 11 is code for own ID inside metadata header
    elif id_type == "DEPENDS_ON":
        id_tuple = (20,21) #binary 20 and 21 is code for dependency ID inside metadata header
    elif id_type == "DEPENDANT_OF":
        id_tuple = (22,23) #binary 22 and 23 is code for dependant ID inside metadata header

    for item in id_tuple: # add id or dependancy code to bin_buffer
        bin_buffer.append(item)

    while uuid > 255: # split a value larger than 255 into binary compatible values, not more than 255
        uuid-=255     # and add it to bin_buffer
        if debug == True:
            print("Append and reduce")
        bin_buffer.append(255)

    if uuid > 0 and uuid <= 255: # add remaining value under 255 to bin_buffer
        if debug == True: 
            print("Less than or equal to 255, adding directly to buffer")
        bin_buffer.append(uuid)

    while len(bin_buffer) < (hbc + 2): # while bin_buffer is less than hbc, header byte count, append 0 to bin_buffer
        bin_buffer.append(0)

    return tuple(bin_buffer)

def header_scalpel(target_file, offset=0):
    """
    header_scalpel() A function used to retrieve a metadata header from an individual note file.

    Required params:
        - target_file; str, file to extract metadata from

    Optional params:
        - offset; int, typically 0 and in current state of NoteCally is not needed for anything.

    Returns:
        - a tuple, a header which is easier to use and process by code maintainers
          semi legible for debugging purposes

          * Also returns the last byte read count by the function as the last parameter
    """
    dep_on = []
    dep_of = []
    file = open(target_file, 'rb')
    file.seek(offset, 0)
    cursor_pos = 0
    uuid = 0
    watchdog = 0 # used for preventing runaway attempt of reading metadata header
                 # if for example attempting to read a petabyte file with nonsense data
    last_byte = 0
    note_name_list = []
    note_name = ""
    while watchdog < 4000:
        byte = file.read(1)
        cursor_pos+=1
        watchdog+=1

        if not byte: # if at end of file
            file.close()
            break

        if int.from_bytes(byte) == 10: # start of id
            byte = file.read(1)
            if int.from_bytes(byte) == 11:
                watchdog = 0
                for _ in range(0,hbc): # the next 32 bytes form current entry' own id
                    value = file.read(1)
                    uuid += int.from_bytes(value)
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 20: # start of depends on
            byte = file.read(1)
            if int.from_bytes(byte) == 21:
                watchdog = 0
                dpon_uuid = 0
                for _ in range(0,hbc):
                    value = file.read(1)
                    dpon_uuid += int.from_bytes(value)
                dep_on.append(dpon_uuid)
                file.seek(cursor_pos,0)
        
        if int.from_bytes(byte) == 22: # start of depends of
            byte = file.read(1)
            if int.from_bytes(byte) == 23:
                watchdog = 0
                dpof_uuid = 0
                for _ in range(0,hbc):
                    value = file.read(1)
                    dpof_uuid += int.from_bytes(value)
                dep_of.append(dpof_uuid)
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 50: # start of date
            byte = file.read(1)
            if int.from_bytes(byte) == 51:
                watchdog = 0
                YYY = 0 # declare hundreds of years as 0
                MM = 0 # declare month as 0
                DD = 0 # declare day as 0
                ML = 0 # declare millenium as 0
                value = file.read(1)
                ML = int.from_bytes(value) # designate first byte as millenium
                for _ in range(0,4): # the next 4 actions:
                    value = file.read(1) # read byte from file
                    YYY += int.from_bytes(value) # previously read byte added to YYY
                value = file.read(1) # read next byte and set MM/month as int from binary (value)
                MM = int.from_bytes(value)
                value = file.read(1) # read next byte and set DD/day as int from binary (value)
                DD = int.from_bytes(value)
                year = (ML,YYY,MM,DD) # a simplified year with millenium, hundred years, month, day
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 40: # start of note name
            byte = file.read(1)
            if int.from_bytes(byte) == 41:
                watchdog = 0
                for _ in range(0,hbc): # the next hbc or 32 bytes form note/entry name
                    value = file.read(1)
                    note_name_list.append(int.from_bytes(value))
                note_name = "".join(bin_decode(note_name_list))
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 30: # header end signiature
            byte = file.read(1)
            if int.from_bytes(byte) == 31:
                last_byte = file.tell()
                file.close()
                return (uuid, tuple(dep_on), tuple(dep_of), note_name, year, last_byte)
                #return: note own uuid, dependancies as tuple, dependants, note name/title, date, where the header ends

def file_len(target_file):
    """
    file_len() A function for determining file length.

    Required params:
        - target_file; str, file for which length must be known

    Returns:
        - cursor; int, length of file
    """
    with open(target_file, 'rb') as file:
        while True:
            byte = file.read(1)
            if not byte:
                cursor = file.tell()
                file.close()
                break
    return cursor

def name_gen(name_input):
    """
    name_gen() A function to generate a binary header
    compatible name with apropriate binary code tag.

    Required params:
        - name_input; str, a name for a note/calendar entry

    Returns:
        - output_data; a tuple which begins with values 40 and 41 and
          contains 34 bytes in total if hbc, header byte count is 32
    """
    if len(name_input) > hbc: # check if length is over header byte count byte limit and if so:
        name = ""
        for i in range(0,hbc): # add characters from name_input to name until header byte count is reached
            name += name_input[i]
    else: # if name is not longer than header byte count limit:
        name = name_input # name is directly the same as name_input
    data = bin_encode(name) # bin_encode is from binhandler.py
    output_data = (40, 41) + data # output data begins with values 40 and 41
    while len(output_data) < (hbc + 2): # while the name portion of the metadata header is shorter than hbc, header byte count:
        output_data += (0,) # add a zero to the tuple output_data
    return output_data

def date_decode(data):
    """
    date_decode() A sub function for turning the 4 value tuple given
    by header_scalpel into a 3 value tuple with a real date e.g. : 2025.6.16

    Required params:
        - data; a 4 value tuple. Example: (2, 25, 6, 16,)

    Returns:
        - a tuple; a "real" date. Example: (2025, 6, 16,)
    """
    year = data[1]
    millenium = data[0] * 1000
    MM = data[2]
    DD = data[3]
    return ((millenium + year), MM, DD)

def read_note(note, parse_text=False):
    """
    read_note() A high-level function intended to be used by as the primary way to read a note.

    Required params:
        - note; str, file name

    Optional params:
        - parse_text; boolean, if false, it returns the header and an empty string instead
          of returning the full contents.
         * This was intended as a feature for an unimplemented nt_index_repair() function
           which would of been a way to add every note in the calendars directory to
           the internal record of all notes: nt_index.dat

    Returns:
        a tuple; which is structured as follows:
        (
            note date, note contents,
            self ID, dependancies of self(unused),
            dependants upon self(unused),
            title or name of note/entry,
            raw date as returned by header_scalpel(),
        )
    """
    text = ""
    scalpel = header_scalpel(note,0)
    if parse_text == True:
        text = "".join(bin_decode(bin_read_precise(note,scalpel[5])))
    note_name = scalpel[3]
    date = date_decode(scalpel[4])
    return (date, text, scalpel[0], scalpel[1], scalpel[2], note_name, scalpel[4])   # needs a name system, copy pasting a block from scalpel in the scalpel function and then using bin_decode to decode name

def write_note(date_in, id_input, name, content, append_db = True, produce_note = True, depon = (), depof = ()): # needs to be figured out properly later
    """
    write_note() A high level function for writing a note/calendar entry.

    Required params:
        - date_in; tuple of 7 values.
          Example: for date 2025.6.16; (2, 25, 0, 0, 0, 6, 16, )

        - id_input; int, if hbc=32: id can be 0-8160.

        - name; str, note/entry name or title.

        - content; str, content of note or entry.

    Optional params:
        - append_db; boolean, Used to toggle off appending to nt_index.dat,
          useful for editing a note or entry.

        - produce_note; boolean, Unused feature, intended for nt_index_repair() and
          importing notes. Both of which are currently unimplemented.

        - depon; tuple with multiple id's, What this entry depends on. (Unused)

        - depof; tuple with multiple id's, Which other entries depend on this one. (Unused)

    Returns:
        - Nothing, only used for writing to files.


    """
    note_name = name_gen(name)
    filename = name.replace(" ","_") + ".bin"
    id_tuple = (id_input,depon,depof) 
    header = header_gen(id_tuple, note_name, date_in)
    output_content = bin_encode(content)

    if append_db == True:
        bin_write("nt_index.dat",header,"ab")

    if produce_note == True:
        bin_write(filename,header,"wb")
        bin_write(filename,output_content,"ab")

def note_db_scan(increment_amount=False, offset=0, amount=4000, target_file="nt_index.dat", debug=False):
    """
    note_db_scan() A high level function intended for reading
    nt_index.dat and extracting information of the various entries
    made by the user.

    Required params:
        - None, does not require parameters.

    Optional params:
        - increment_amount; boolean, intended as a toggle for enabling limiting the
          memory footprint of the resulting output of note_db_scan().
        
        - offset; int, where to begin reading/searching for entries headers,
          and associated metadata

        - amount; int, limit to amount of bytes to scan through in specified file,
          usually nt_index.dat.

        - target_file; str, file to read, with NoteCally always: nt_index.dat.

        - debug; boolean, (Unused)

    Returns:
        - a tuple; a semi readable tuple, used by menu.py.
          Contains keywords and associated values, structured as follows:
          (
            ('UUID', 1, 'TITLE', 'hello world', 'YEAR', (2, 25, 6, 16), 'BRK'), 
          0)
    """
    data_stream = []
    watchdog = 0
    amount_incr = 0
    with open(target_file, 'rb') as file:
        file.seek(offset, 0)
        while watchdog < 4000 and amount_incr < amount:
            watchdog += 1
            if increment_amount == True: # increment amount is used to limit how far nt_index.dat is scanned.
                amount_incr += 1
            byte = file.read(1)
            if not byte: # if no valid bytes are left, cease the while loop.
                file.close()
                break

            if int.from_bytes(byte) == 30: # 10 11 self, 20 21 dep on, 22 23 dep of, 40 41 name, 50 51 date, 30 31 EOF
                cursor_restore = file.tell()
                value = file.read(1)
                if int.from_bytes(value) == 31:
                    data_stream.append("BRK") # 30 and 31 indicate the end of a given entry' binary header
                    watchdog = 0
                else:
                    file.seek(cursor_restore,0)

            elif int.from_bytes(byte) == 10:
                cursor_restore = file.tell()
                value = file.read(1)
                if int.from_bytes(value) == 11:
                    data_stream.append("UUID") # 10 and 11 indicates next 32/hbc value are reserved for entry' own id
                    watchdog = 0
                    uuid = 0
                    for _ in range(0,hbc):
                        value = file.read(1)
                        uuid += int.from_bytes(value)
                    data_stream.append(uuid)
                else:
                    file.seek(cursor_restore,0)

            elif int.from_bytes(byte) == 20:
                cursor_restore = file.tell()
                value = file.read(1)
                if int.from_bytes(value) == 21:
                    data_stream.append("DEP ON") # 20 and 21 indicates next 32/hbc value are reserved for id' of which current entry depends on
                    watchdog = 0
                    dpon_uuid = 0
                    for _ in range(0,hbc):
                        value = file.read(1)
                        dpon_uuid += int.from_bytes(value)
                    data_stream.append(dpon_uuid)
                else:
                    file.seek(cursor_restore,0)

            elif int.from_bytes(byte) == 22:
                cursor_restore = file.tell()
                value = file.read(1)
                if int.from_bytes(value) == 23:
                    data_stream.append("DEP OF") # 22 and 23 indicates next 32/hbc value are reserved for id' of entries that depend on current entry
                    watchdog = 0
                    dpof_uuid = 0
                    for _ in range(0,hbc):
                        value = file.read(1)
                        dpof_uuid += int.from_bytes(value)
                    data_stream.append(dpof_uuid)
                else:
                    file.seek(cursor_restore,0)
            
            elif int.from_bytes(byte) == 40:
                cursor_restore = file.tell()
                value = file.read(1)
                if int.from_bytes(value) == 41:
                    data_stream.append("TITLE") # 40 and 41 indicate the next 32 or hbc amount of bytes reserved for title.
                    watchdog = 0
                    note_name_list = []
                    for _ in range(0,hbc): # the next (hbc, typically 32) bytes are reserved for title/name of entry
                        value = file.read(1)
                        note_name_list.append(int.from_bytes(value)) # a list of the next hbc or 32 values is collected into note_name_list
                    note_name = "".join(bin_decode(note_name_list)) # note name is a string returned from bin_decode() found in binhandler.py, with input as note_name_list
                    data_stream.append(note_name)
                else:
                    file.seek(cursor_restore,0)
            
            elif int.from_bytes(byte) == 50:
                cursor_restore = file.tell()
                value = file.read(1)
                if int.from_bytes(value) == 51: # 50 and 51 are reserved for the date.
                    YYY = 0 # hundreds of years
                    MM = 0 # month
                    DD = 0 # day
                    ML = 0 # millenium
                    value = file.read(1)
                    ML = int.from_bytes(value) # first value of year is always millenium
                    for _ in range(0,4): # the next 4 bytes are added together up to a theoretical maximum of 1020 but in practice max 999
                        value = file.read(1)
                        YYY += int.from_bytes(value)
                    value = file.read(1)
                    MM = int.from_bytes(value) # 6th value is month
                    value = file.read(1)
                    DD = int.from_bytes(value) # 7th value is day
                    year = (ML,YYY,MM,DD) # combination of the values in a year into a 4 value tuple
                    data_stream.append("YEAR") # year tag added to data_stream
                    watchdog = 0
                    data_stream.append(year) # year added to data_stream
                    file.seek(cursor_restore,0)
                else:
                    file.seek(cursor_restore,0)

    return (tuple(data_stream),amount_incr)
