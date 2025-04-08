#! /usr/bin/python3

screen = []
screen_width = []

def overlay_sys_init(col, lin): 
    global max_width 
    global max_height
    max_width = col
    max_height = (lin - 1)
    
    while len(screen_width) < max_width:
        screen_width.append(" ")
    while len(screen) < max_height:
        screen.append(screen_width[:])

    return max_height, max_width

def screen_dbg_tape(tape = True, pluses = True):
    xten = []
    yten = []
    index = 0
    i = 0
    while index <= (max_width - 1):
        if i < 9:
            i+=1
        else:
            i=0
        if tape == True:
            screen_write(index,0,str(i))
        if i == 0:
            if tape == True:
                screen_write(index,1,"|")
            xten.append(index)
        index+=1

    index = 0
    i = 0
    while index <= (max_height - 1):
        if i < 9:
            i+=1
        else:
            i=0
        if tape == True:
            screen_write(0,index,str(i))
        if i == 0:
            if tape == True:
                screen_write(1,index,"-")
            yten.append(index)
        index+=1
    
    if pluses == True:
        y = 0
        while y < len(yten):
            x = 0
            while x < len(xten):
                screen_write(xten[x], yten[y], "*")
                x+=1
            y+=1

def screen_print():
    for line in screen:
        print(''.join(line))

def screen_write(x, y, char): # add protection for eol markers
    screen[y][x] = char

def screen_clear():
    i = 0
    while i < max_height:
        screen[i] = screen_width[:]
        i+=1

################################################

class Window:
    def __init__(self, win_id, corner1x, corner1y, size=10, corner2x=-1, corner2y=-1):
        self.c1x = corner1x
        self.c1y = corner1y
        self.c2x = corner2x
        self.c2y = corner2y
        self.win_id = win_id
        self.last_content = ""
        self.cont_cursor = (0,0)
        self.content_history = []

        if self.c2x == -1:
            self.c2x = (self.c1x + (size * 4))
            self.c2y = (self.c1y + size)
        elif self.c2y == -1:
            self.c2x = (self.c1x + (size * 4))
            self.c2y = (self.c1y + size)

        self.win_width = ((self.c2x - self.c1x)-1)
        self.win_height = ((self.c2y - self.c1y)-1)

    def win_upd_cont(self, content, strict=True, auto_newline=True, content_hist_bool=False):
        if self.last_content[-1] == " " or content[0] == " ":
            new_cont = self.last_content + content
        else:
            new_cont = self.last_content + " " + content

        self.win_raw_cont(new_cont, strict, auto_newline, content_hist_bool)

    def win_segment_cont(self, segment_list):
        if self.last_content == "":
            self.last_content = " "
        for segment in segment_list:
            if self.cont_cursor[0] + len(segment) < (self.c2x - 1):
                self.win_upd_cont(segment, True, False)
            else:
                self.win_upd_cont("╳" + f" {segment}", True, False)


    def win_raw_cont(self, content, strict=True, auto_newline=True, content_hist_bool=False):
        self.last_content = content

        if content_hist_bool == True:
            content_history.append(content)

        if strict == True:
            y=1
            x=1
            x_offset = 1
        else:
            y=0
            x=0
            x_offset = 0

        for char in content: # ╳ NOT THE LETTER X; is a control character used to initialize newline in window
            if char == "╳" or char == "\n":
                y += 1
                x = x_offset
                self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
            elif char == "┼": # Allows moving upwards
                y -= 1
                x = x_offset
                self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
            elif char == "╱": # ╲ NOT FORWARDSLASH; is a control character used to move backwards a single character in the terminal 
                x-=1
                self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
            elif x >= ((self.c2x-1) - self.c1x) and auto_newline == True and strict == True:
                screen_write(self.c1x + x, self.c1y + y, "-")
                self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
                x = x_offset
                y+=1
                screen_write(self.c1x + x, self.c1y + y, char)
                self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
                x+=1
            elif char == "╲": # ╲ NOT BACKSLASH; is a control character used to move forward a single character in the terminal 
                x+=1
            else:
                if strict==True and x < (self.c2x - self.c1x) and y < (self.c2y - self.c1y):
                    screen_write(self.c1x + x, self.c1y + y, char)
                    self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
                if strict==False:
                    screen_write(self.c1x + x, self.c1y + y, char)
                    self.cont_cursor = ((self.c1x + x) + 1, self.c1y + y)
                x+=1
        
    def win_draw(self, overwrite_content=True, vert="│", horiz="─", ul_cor="┌", ur_cor="┐", ll_cor="└", lr_cor="┘"):
        iy = self.c1y
        while iy <= self.c2y:
            screen_write(self.c1x,iy,vert)
            screen_write(self.c2x,iy,vert)
            ix = self.c1x
            while ix <= self.c2x:
                if ix == self.c1x:
                    screen_write(ix,self.c1y,ul_cor)
                    screen_write(ix,self.c2y,ll_cor)
                elif ix == self.c2x:
                    screen_write(ix,self.c1y,ur_cor)
                    screen_write(ix,self.c2y,lr_cor)
                elif ix != self.c1x and ix != self.c2x and iy != self.c1y and iy != self.c2y and overwrite_content == True:
                    screen_write(ix,iy," ")
                else:
                    screen_write(ix,self.c1y,horiz)
                    screen_write(ix,self.c2y,horiz)
                ix += 1
            iy += 1

    def win_ret_size(self):
        width = self.win_width
        height = self.win_height
        val = (width, height)
        return val

    def win_ret_relat_pos(self, x="", y=""):
        if y == "" or x == "":
            val = ((self.c1x,self.c1y),(self.c2x,self.c2y))
            x = 0
            y = 0
        else: 
            x_pos = self.c1x + x
            y_pos = self.c1y + y
            val = (x_pos, y_pos)

        if y < 0 or x < 0:
            return -1
        elif y > (self.win_height + 1):
            return 2
        elif x > (self.win_width + 1):
            return 1
        elif y > (self.win_height + 1) and x > (self.win_width + 1):
            return 3
        else:
            return val

    def win_clear(self, destr_brdr=False):
        ctrl_value = 0
        if destr_brdr == False:
            ctrl_value = 1
        iy = self.c1y + ctrl_value
        while iy <= self.c2y - ctrl_value:
            ix = self.c1x + ctrl_value
            while ix <= self.c2x - ctrl_value:
                screen_write(ix,iy," ")
                ix += 1
            iy += 1

# ─│┌┐└┘├┤┬┴┼█░▒╱╲╳

# ╭╮╯╰

#    ─ 	━ 	│ 	┃ 	┄ 	┅ 	┆ 	┇ 	┈ 	┉ 	┊ 	┋ 	┌ 	┍ 	┎ 	┏
# 	┐ 	┑ 	┒ 	┓ 	└ 	┕ 	┖ 	┗ 	┘ 	┙ 	┚ 	┛ 	├ 	┝ 	┞ 	┟
# 	┠ 	┡ 	┢ 	┣ 	┤ 	┥ 	┦ 	┧ 	┨ 	┩ 	┪ 	┫ 	┬ 	┭ 	┮ 	┯
# 	┰ 	┱ 	┲ 	┳ 	┴ 	┵ 	┶ 	┷ 	┸ 	┹ 	┺ 	┻ 	┼ 	┽ 	┾ 	┿
# 	╀ 	╁ 	╂ 	╃ 	╄ 	╅ 	╆ 	╇ 	╈ 	╉ 	╊ 	╋ 	╌ 	╍ 	╎ 	╏
# 	═ 	║ 	╒ 	╓ 	╔ 	╕ 	╖ 	╗ 	╘ 	╙ 	╚ 	╛ 	╜ 	╝ 	╞ 	╟
# 	╠ 	╡ 	╢ 	╣ 	╤ 	╥ 	╦ 	╧ 	╨ 	╩ 	╪ 	╫ 	╬ 	╭ 	╮ 	╯
# 	╰ 	╱ 	╲ 	╳ 	╴ 	╵ 	╶ 	╷ 	╸ 	╹ 	╺ 	╻ 	╼ 	╽ 	╾ 	╿ 

# 	▀ 	▁ 	▂ 	▃ 	▄ 	▅ 	▆ 	▇ 	█ 	▉ 	▊ 	▋ 	▌ 	▍ 	▎ 	▏
# 	▐ 	░ 	▒ 	▓ 	▔ 	▕ 	▖ 	▗ 	▘ 	▙ 	▚ 	▛ 	▜ 	▝ 	▞ 	▟ 