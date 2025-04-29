#! /bin/python3

from binhandler import bin_encode, bin_decode, bin_write, bin_read, binary_sys_init, bin_read_precise

hbc = 32 # header byte count

binary_sys_init(False,0,False)

def header_gen(id_input, name_input, date_input): # tuple; first index contains only own uuid, second index contains potential dependencies, third index contains items which depend on self
    header_self = id_gen("SELF",id_input[0])
    header_dep_on = []
    header_dep_of = []
    if len(id_input) > 1:
        for item in id_input[1]:
            header_dep_on.append(id_gen("DEPENDS_ON",item))
    if len(id_input) == 3:
        for item in id_input[2]:
            header_dep_of.append(id_gen("DEPENDANT_OF",item))
    return header_self + tuple(header_dep_on) + tuple(header_dep_of) + name_input + (50,51) + date_input + (30,31)

def id_gen(id_type,uuid,debug=False):
    bin_buffer = []

    if uuid > (255*hbc):
        raise ValueError(f"Given UUID is too large. Maximum value: (hbc * 255 -> {hbc*255}) NOT {uuid}")

    if id_type == "SELF":
        id_tuple = (10,11)
    elif id_type == "DEPENDS_ON":
        id_tuple = (20,21)
    elif id_type == "DEPENDANT_OF":
        id_tuple = (22,23)

    for item in id_tuple:
        bin_buffer.append(item)

    while uuid > 255:
        uuid-=255
        if debug == True:
            print("Append and reduce")
        bin_buffer.append(255)

    if uuid > 0 and uuid <= 255:
        if debug == True: 
            print("Less than or equal to 255, adding directly to buffer")
        bin_buffer.append(uuid)

    while len(bin_buffer) < (hbc + 2):
        bin_buffer.append(0)

    return tuple(bin_buffer)

def header_scalpel(target_file, offset=0):
    dep_on = []
    dep_of = []
    file = open(target_file, 'rb')
    file.seek(offset, 0)
    cursor_pos = 0
    uuid = 0
    watchdog = 0
    last_byte = 0
    note_name_list = []
    note_name = ""
    while watchdog < 4000:
        byte = file.read(1)
        cursor_pos+=1
        watchdog+=1

        if int.from_bytes(byte) == 10: # start of id
            byte = file.read(1)
            if int.from_bytes(byte) == 11:
                watchdog = 0
                for _ in range(0,hbc):
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

        if int.from_bytes(byte) == 50:
            byte = file.read(1)
            if int.from_bytes(byte) == 51:
                watchdog = 0
                ML = 0
                YYY = 0
                MM = 0
                DD = 0
                for _ in range(0,1):
                    value = file.read(1)
                    ML += int.from_bytes(value)
                for _ in range(0,4):
                    value = file.read(1)
                    YYY += int.from_bytes(value)
                value = file.read(1)
                MM = int.from_bytes(value)
                value = file.read(1)
                DD = int.from_bytes(value)
                year = (ML,YYY,MM,DD)
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 40: # start of depends on
            byte = file.read(1)
            if int.from_bytes(byte) == 41:
                watchdog = 0
                for _ in range(0,hbc):
                    value = file.read(1)
                    note_name_list.append(int.from_bytes(value))
                note_name = "".join(bin_decode(note_name_list))
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 30: # eof signiature
            byte = file.read(1)
            if int.from_bytes(byte) == 31:
                last_byte = file.tell()
                file.close()
                return (uuid, tuple(dep_on), tuple(dep_of), note_name, year, last_byte)
                #return: note own uuid, dependancies as tuple, dependants, note name/title, date, where the header ends

def file_len(target_file):
    with open(target_file, 'rb') as file:
        while True:
            byte = file.read(1)
            if not byte:
                cursor = file.tell()
                file.close()
                break
    return cursor

def name_gen(name_input):
    if len(name_input) > hbc:
        name = ""
        for i in range(0,hbc):
            name += name_input[i]
    else:
        name = name_input
    data = bin_encode(name)
    output_data = (40, 41) + data
    while len(output_data) < (hbc + 2):
        output_data += (0,)
    return output_data

def date_decode(data):
    year = data[1]
    millenium = data[0] * 1000
    MM = data[2]
    DD = data[3]
    return ((millenium + year), MM, DD)

def read_note(note, parse_text=False):
    text = ""
    scalpel = header_scalpel(note,0)
    if parse_text == True:
        text = "".join(bin_decode(bin_read_precise(note,scalpel[-1])))
    note_name = scalpel[3]
    date = date_decode(scalpel[4])
    return (date, text, scalpel[0], scalpel[1], scalpel[2], note_name)   # needs a name system, copy pasting a block from scalpel in the scalpel function and then using bin_decode to decode name

def write_note(date_in, id_input, name, content, depon = (), depof = ()): # needs to be figured out properly later
    note_name = name_gen(name)
    filename = name.replace(" ","_") + ".dat"
    id_tuple = (id_input,depon,depof) 
    header = header_gen(id_tuple, note_name, date_in)
    output_content = bin_encode(content)

    #bin_write("nt_index.bin",header,"ab")
    #print(header)
    bin_write(filename,header,"wb")
    bin_write(filename,output_content,"ab")

#def note_db_scan(target_file="nt_index.bin", debug=False):


    





    #database = []
    #length = file_len(target_file)
    #i=0
    #offset = 0
    #while i < length:
    #    data = header_scalpel(target_file, offset)
    #    offset = data[-1]
    #    database.append(data)
    #    print(offset)
    #    print(database)
    #    i += offset

#write_note((2,25,0,0,0,4,24), 667,":(","this didnt work out as i had hoped")
#write_note((2,26,0,0,0,8,20), 668,"get off my lawn","this didnt work")
#write_note((2,27,0,0,0,6,31), 669,"now","this")
#print(bin_read("Hello_World_this_is_my_note.dat"))
#print(read_note("yippee_third.dat",True))

#print(file_len("nt_index.bin"))

#note_db_scan()

#print(bin_read("nt_index.bin"))

print(header_scalpel("nt_index.bin"))
print(header_scalpel("nt_index.bin",78))