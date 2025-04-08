#! /bin/python3

# ─│┌┐└┘├┤┬┴┼█░▒╱╲╳
bin_characters = [
"╳","╱","╲","▒","░","█","┼","┴","Q","W","E","R","T","V","k","┘","?",
"Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Z","X","C",
"B","N","M","p","o","i","u","y","t","r","e","w","q","a","s","d","l",
"j","h","g","f","z","m","x","n","c","b","v",":",";","^","┬","┤","├",
"└","┐","┌","│","─","!","'",'"',"#","¤","%","&","/","(",")"," ","=",
"-","_",".",",","<",">","|","@","£","$","€","{","}","+","\\","*","[",
"]","\n",
]

def binary_sys_init(debug=False): # IMPORTANT: MUST be called before binary operations can be performed
    i=0
    global bin_decimals
    bin_decimals = []
    for index in bin_characters:
        bin_decimals.append(255 - i)
        i+=1
    if debug == True:
        print("Binary Decimals list length:" + str(len(bin_decimals)))
        print("Character list length:" + str(len(bin_characters)))
        print("Last Binary Decimal code indexed:" + str(255 - i))

def bin_encoder(target_file, file_content):
    file_data = list(file_content)
    character_index_data=[]
    bin_op_buffer = []
    i=0
    while i < len(file_data):
        character_index_data.append(bin_characters.index(file_data[i]))
        i+=1
    i=0
    while i < len(character_index_data):
        bin_op_buffer.append(bin_decimals[character_index_data[i]])
        i+=1
    bin_array = bytes(bin_op_buffer)
    file = open(target_file,"ab")
    file.write(bin_array)
    file.close()

def bin_decoder(target_file):
    character_index_data = []
    txt_op_buffer = []
    txt_print_buffer = []
    with open(target_file, 'rb') as file:
        while True:
            byte = file.read(1)
            if not byte:
                file.close()
                break
            character_index_data.append(int.from_bytes(byte))
    i=0
    while i < len(character_index_data):
        txt_op_buffer.append(bin_decimals.index(character_index_data[i]))
        i+=1
    i=0
    while i < len(txt_op_buffer):
        txt_print_buffer.append(bin_characters[txt_op_buffer[i]])
        i+=1
    print(''.join(txt_print_buffer))