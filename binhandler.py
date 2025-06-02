#! /bin/python3

bin_characters = (
"╳","╱","å","1","9","3","╲","▒","░","█","┼","┴","Q","W","E","R","T","V","k","┘","?",
"Y","U","I","Å","O","P","A","S","D","F","G","H","J","7","K","L","Z","X","C",
"B","N","M","p","8","o","Ä","i","0","u","y","2","t","ä","r","6","e","w","q","a","s","d","l",
"j","h","g","5","f","z","m","x","n","c","b","v",":",";","^","┬","┤","├",
"└","┐","┌","│","─","!","'",'"',"4","#","¤","%","ö","&","/","(",")"," ","=",
"-","_",".",",","<",">","|","@","£","$","€","{","}","Ö","+","\\","*","[",
"]","\n",
)

def binary_sys_init(reverse=False,offset=0,debug=False): # IMPORTANT: MUST be called before binary operations can be performed
    i=0
    global bin_decimals
    bin_decimals = []
    for _ in bin_characters:
        if reverse == False:
            bin_decimals.append(255 - i - offset)
        else:
            bin_decimals.append(i + offset)
        i+=1
    if debug == True:
        print("Binary Decimals list length:" + str(len(bin_decimals)))
        print("Character list length:" + str(len(bin_characters)))
        print("Last Binary Decimal code indexed:" + str(255 - i))

def bin_encode(content):
    bin_op_buffer = []
    i=0
    while i < len(content):
        bin_op_buffer.append(bin_decimals[bin_characters.index(content[i])])
        i+=1
    return tuple(bin_op_buffer)

def bin_write(target_file, file_content, mode="ab"):
    with open(target_file,mode) as file:
        file.write(bytes(file_content))
        file.close()

def bin_read(target_file, debug=False):
    character_index_data = []
    with open(target_file, 'rb') as file:
        while True:
            byte = file.read(1)
            if not byte:
                file.close()
                break
            character_index_data.append(int.from_bytes(byte))
    return tuple(character_index_data)

def bin_read_precise(target_file, offset=0, amount=-1, debug=False):
    character_index_data = []
    with open(target_file, 'rb') as file:
        file.seek(offset,0)
        i=0
        while i < amount or amount == -1:
            byte = file.read(1)
            if not byte:
                file.close()
                break
            character_index_data.append(int.from_bytes(byte))
            i+=1
    return tuple(character_index_data)
    
def bin_decode(input_data, debug=False):
    txt_print_buffer = []
    i=0
    while i < len(input_data):
        if input_data[i] == 0:
            break
        txt_print_buffer.append(bin_characters[bin_decimals.index(input_data[i])])
        i+=1
    if debug == True:
        print(''.join(txt_print_buffer))
    return tuple(txt_print_buffer)
