#! /bin/python3

from binhandler import bin_encode, bin_decode, bin_write, bin_read, binary_sys_init

sig_start = "▒█░"
sig_end = "█▒░"

def signed_data(target_file, content, mode):
    if mode == "SIGN" or mode == "S":
        parse_data = sig_start + content + sig_end
    if mode == "INSERT" or mode == "I":
        parse_data = content
    if mode == "BEGIN" or mode == "B":
        parse_data = sig_start
    if mode == "CEASE" or mode == "C":
        parse_data = sig_end

    data = bin_encode(parse_data)
    bin_write(target_file, data)

def header_scalpel(target_file, offset=0):
    dep_on = []
    dep_of = []
    file = open(target_file, 'rb')
    file.seek(offset, 0)
    cursor_pos = 0
    uuid = 0
    last_byte = 0
    i=0
    while True:
        byte = file.read(1)
        cursor_pos+=1

        if int.from_bytes(byte) == 10: # start of id
            byte = file.read(1)
            if int.from_bytes(byte) == 11:
                for _ in range(0,8):
                    value = file.read(1)
                    uuid += int.from_bytes(value)
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 20: # start of depends on
            byte = file.read(1)
            if int.from_bytes(byte) == 21:
                dpon_uuid = 0
                for _ in range(0,8):
                    value = file.read(1)
                    dpon_uuid += int.from_bytes(value)
                dep_on.append(dpon_uuid)
                file.seek(cursor_pos,0)

        if int.from_bytes(byte) == 30: # eof signiature
            byte = file.read(1)
            if int.from_bytes(byte) == 31:
                last_byte = file.tell()
                file.close()
                return (uuid, dep_on, last_byte)

        if int.from_bytes(byte) == 20: # start of depends on
            byte = file.read(1)
            if int.from_bytes(byte) == 21:
                dpof_uuid = 0
                for _ in range(0,8):
                    value = file.read(1)
                    dpof_uuid += int.from_bytes(value)
                dep_of.append(dpof_uuid)
                file.seek(cursor_pos,0)

#bin_write("binary.values",[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,10,11,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20,21,1,1,1,1,1,1,1,1,0,0,0,100,105,0,0,20,21,2,2,2,2,2,2,2,2,0,0,0,0,0,0,30,31,], "wb")
control_val = 94

print("scalpel:", header_scalpel("binary.values",0))
print(bin_read("binary.values"))
print("length: ",len(bin_read("binary.values")))
print(bin_read("binary.values")[control_val-1])