#! /bin/python3

from binhandler import bin_encoder, bin_decoder, binary_sys_init
import os
from overlaysystem import screen_dbg_tape, overlay_sys_init, screen_print, Window, screen_write

term_size = os.get_terminal_size()
term_width = (term_size.columns - 1)
term_height = (term_size.lines - 2)

term_width_frth = (int(term_width / 4))

binary_sys_init() # debug True or False (Empty = False)
overlay_sys_init(term_size.columns, term_size.lines)

control_window = Window(1, 0, 0, 0, term_width_frth, (term_height - 2))
control_window.win_draw()

viewport_main = Window(2, (term_width_frth + 1), 0, 0, term_width, (term_height - 8))
viewport_main.win_draw()

statusbar = Window(3, (term_width_frth + 1), (term_height - 7), 0, term_width, (term_height - 2))
statusbar.win_draw()

statusbar.win_segment_cont(["Commands | :help/h (Help)",":rd",":wt",":dir",":sv",":ud",":del"])

screen_print()