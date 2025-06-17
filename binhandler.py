#! /bin/python3
"""
Binary handler.

A set of generic functions for encoding-writing, decoding-reading
binary.
With helper functions for writing specially binary encoded text to
avoid adding plain text to a given file.
"""
bin_characters = ( # A character table by which files are encoded with, adding a character here will make it usable
"╳","╱","å","1","9","3","╲","▒","░","█","┼","┴","Q","W","E","R","T","V","k","┘","?",
"Y","U","I","Å","O","P","A","S","D","F","G","H","J","7","K","L","Z","X","C",
"B","N","M","p","8","o","Ä","i","0","u","y","2","t","ä","r","6","e","w","q","a","s","d","l",
"j","h","g","5","f","z","m","x","n","c","b","v",":",";","^","┬","┤","├",
"└","┐","┌","│","─","!","'",'"',"4","#","¤","%","ö","&","/","(",")"," ","=",
"-","_",".",",","<",">","|","@","£","$","€","{","}","Ö","+","\\","*","[",
"]","\n",
)

def binary_sys_init(reverse=False,offset=0,debug=False): # IMPORTANT: MUST be called before text to binary operations can be performed
    """
    binary_sys_init() A function for initializing text to binary encoding or
    binary to text decoding operations.

    Required params:
        - None.

    Optional params:
        - reverse; boolean, if true start indexing characters in bin_characters list
          from (0+offset) and upwards, instead of (255-offset) and downwards

        - offset; int, an offset for where to begin indexing bin_characters list
          helps make encodings incompatible easier along with reverse parameter

        - debug; boolean, true enables printing debug information to console,
          such as: character list(bin_characters) length,
          decimal list(bin_decimals) length which is generated with thi function,
          last decimal value assigned to bin_decimals list.
    
    Returns:
        - Nothing*
          * Creates a global variable within binhandler' scope called bin_decimals
    """
    i=0
    global bin_decimals # initialise global value used by bin_encode() and bin_decode()
    bin_decimals = []
    for _ in bin_characters: # for every character in bin_characters:
        if reverse == False:
            bin_decimals.append(255 - i - offset) # if reverse is false, append decimal values from 255 and downwards
        else:
            bin_decimals.append(i + offset) # if reverse is true, append decimal values from 0 upwards
        i+=1
    if debug == True:
        print("Binary Decimals list length:" + str(len(bin_decimals)))
        print("Character list length:" + str(len(bin_characters)))
        print("Last Binary Decimal code indexed:" + str(255 - i))

def bin_encode(content):
    """
    bin_encode() encode a string(aka content) to
    decimal values corresponding to binary values.

    Required params:
        - content; str, a string to encode to decimals and be ready to use with bin_write() .

    Returns:
        - a tuple; containing decimal values ready to use with bin_write() .
    """
    bin_op_buffer = []
    i=0
    while i < len(content): # iterate through content
        bin_op_buffer.append(bin_decimals[bin_characters.index(content[i])]) # append decimal value to bin_op_buffer based on content' character' index in
        i+=1                                                                 # bin_characters by taking index of single character in content and appending whats found in bin_decimals at same index as the single character
    return tuple(bin_op_buffer)

def bin_write(target_file, file_content, mode="ab"):
    """
    bin_write() write a tuple(file_content) with decimal values to a file(target_file).

    Required params:
        - target_file, str, file to write into.

        - file_content, tuple, a tuple with decimal values corresponding to binary values (0-255).

    Optional params:
        - mode; str, set mode to something else besides "ab"(append binary)

    Returns:
        - Nothing. Used to edit and write files.
    """
    with open(target_file,mode) as file: # open file and write to it, then close the file
        file.write(bytes(file_content))
        file.close()

def bin_read(target_file, debug=False):
    """
    bin_read() read a binary file(target_file)

    Required params:
        - target_file; str, a filename which to read.

    Optional params:
        - debug; boolean, Unimplemented, not actually
          used for anything.

    Returns:
        - a tuple; a tuple containing decimal values corresponding
          to binary values in target_file.
    """
    character_index_data = []
    with open(target_file, 'rb') as file:
        while True: # while still reading file:
            byte = file.read(1) # read the next byte
            if not byte:
                file.close() # if not a valid byte, aka end of file reached close file and break while loop
                break
            character_index_data.append(int.from_bytes(byte)) # append decimal values to character_index_data from binary file
    return tuple(character_index_data)

def bin_read_precise(target_file, offset=0, amount=-1, debug=False):
    """
    bin_read_precise() a precision binary reading function capable
    of reading from a given offset for any amount or to end of target_file

    Required params:
        - target_file; str, filename of file to read.
    
    Optional params:
        - offset; int, offset where to begin reading in target_file

        - amount; int, limit amount to read, or set to infinite with -1

        - debug; boolean, Unused, not implemented.

    Returns:
        - tuple; contains decimal values corresponding to binary values in target_file
    """
    character_index_data = []
    with open(target_file, 'rb') as file:
        file.seek(offset,0)
        i=0
        while i < amount or amount == -1: # while i is less than amount, or amount is set to -1:
            byte = file.read(1) # read next byte in target_file
            if not byte:
                file.close() # if end of file reached, close file and break while loop.
                break
            character_index_data.append(int.from_bytes(byte)) # append decimal value from byte in binary file to character_index_data list
            i+=1
    return tuple(character_index_data)
    
def bin_decode(input_data, debug=False):
    """
    bin_decode() a function to decode text which has
    been binary encoded.

    Required params:
        - input_data; tuple, a tuple with decimal values
          corresponding to bin_decimals indexes and bin_characters indexes.
        
    Optional params:
        - debug; boolean, enables printing decoded binary text to console.

    Returns:
        - tuple; contains characters found in bin_characters which have
          been decoded based off of index data retrieved from bin_decimals.
    """
    txt_print_buffer = []
    i=0
    while i < len(input_data): # while i is less than the input_data being decoded:
        if input_data[i] == 0: # if input data is 0 break while loop and stop attempting to decode
            break
        txt_print_buffer.append(bin_characters[bin_decimals.index(input_data[i])]) # append a character from bin_characters based on index in bin_decimals
        i+=1 # iterate i
    if debug == True:
        print(''.join(txt_print_buffer)) # if debug is true: print the contents of txt_print_buffer concatenated to string.
    return tuple(txt_print_buffer)
