import sys
import os
import re
from time import time, sleep
from random import randint
from copy import deepcopy
import keyboard
import logging
import winsound
import threading
from ast import literal_eval
from graphics import GraphWin, Rectangle, Point
from chip8_engine import Chip8

chip_8 = Chip8()

# original COSMAC VIP emulation
orig = True

# original COSMAC VIP incrementation of index variable
inc = False

# debug mode
debug = False

# line by line mode
lbl = False

# rom filename
file_name = sys.argv[1]

# fn extracts the specific filename
fn = deepcopy(file_name)
while fn.find("/") != -1:
    fn = fn[fn.find("/") + 1:]
if fn.find(".") != -1:
    fn = fn[:fn.find(".")]

# additional commands
if len(sys.argv) > 2:
    for comm in sys.argv[2:]:
        if comm == "-o":
            orig = False
        elif comm == "-i":
            inc = True
        elif comm == "-d":
            debug = True
        elif comm == "-l":
            lbl = True

# change logging level if debugging
if debug:
    loglevel = logging.INFO
else:
    loglevel = logging.WARNING
logger = logging.getLogger()
logger.setLevel(loglevel)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(loglevel)
handler.terminator = ""
logger.addHandler(handler)

# load rom into memory
with open(file_name, 'rb') as f:
    file_content = f.read()
    for i in range(len(file_content)):
        chip_8.memory[0x200 + i] = file_content[i]
    
# create canvas
win = GraphWin(title=fn, width=64*16, height=32*16, autoflush=False)
win.setCoords(0, 0, 64, 32)

# sound function
def beep(length):
    winsound.Beep(750, int(length * 1000 / 60))

# interpreter loop
while True:
    # cycle timing
    cycle = 1/700
    if lbl:
        input()

    # fetch instruction
    instr = (chip_8.memory[chip_8.pc] << 8) | chip_8.memory[chip_8.pc + 1]
    chip_8.pc += 2
    
    # debugging print statements
    logging.info(f"0x{chip_8.pc - 2:03X}: 0x{instr:04X}\t")
    for i in range(len(chip_8.reg)):
        logging.info(f"v{i:X}: 0x{chip_8.reg[i]:02X} ")
    logging.info("\nstk: ")
    for s in chip_8.stk:
        logging.info(f"0x{s:03X}, ")
    logging.info("\n")

    # nibble information
    op = (instr >> 0xC) & 0xF # first nibble
    x = (instr >> 0x8) & 0xF # second nibble
    y = (instr >> 0x4) & 0xF # third nibble
    n = instr & 0xF # fourth nibble
    nn = instr & 0xFF # second byte (8 bit number)
    nnn = instr & 0xFFF # second nibble plus second byte (12 bit memory address)

    # decode and execute instruction
    tick = time()
    if instr == 0x0000:
        # end of program
        logging.info("program is over\n")
        break
    elif instr == 0x00E0:
        # clear screen
        logging.info("clear the screen\n")
        cycle = 0
        chip_8.display = [0x0 for i in chip_8.display]
        for i in win.items[:]:
            i.undraw()
        win.update()
    elif instr == 0x00EE:
        # pop stack
        logging.info("pop stack\n")
        cycle = 0
        chip_8.pc = chip_8.stk.pop()
    elif op == 0x1:
        # jump to nnn
        logging.info(f"jump to 0x{nnn:02X}\n")
        cycle = 0
        if chip_8.pc - 2 == nnn:
            # loops on last instruction
            logging.info("program complete\n")
            break
        chip_8.pc = nnn
    elif op == 0x2:
        # call nnn, push current pc to stack
        logging.info(f"push 0x{chip_8.pc:03X} to stack and jump to 0x{nnn:03X}\n")
        cycle = 0
        chip_8.stk.append(chip_8.pc)
        chip_8.pc = nnn
    elif op == 0x3:
        # this and next three are skips
        logging.info(f"if v{x:X} == 0x{nn:02X}, then skip\n")
        cycle = 0
        if chip_8.reg[x] == nn:
            chip_8.pc += 2
    elif op == 0x4:
        logging.info(f"if v{x:X} != 0x{nn:02X}, then skip\n")
        cycle = 0
        if chip_8.reg[x] != nn:
            chip_8.pc += 2
    elif op == 0x5 and n == 0x0:
        logging.info(f"if v{x:X} == v{y:X}, then skip\n")
        cycle = 0
        if chip_8.reg[x] == chip_8.reg[y]:
            chip_8.pc += 2
    elif op == 0x9 and n == 0x0:
        logging.info(f"if v{x:X} != v{y:X}, then skip\n")
        cycle = 0
        if chip_8.reg[x] != chip_8.reg[y]:
            chip_8.pc += 2
    elif op == 0x6:
        # set
        logging.info(f"set v{x:X} to 0x{nn:02X}\n")
        cycle = 0
        chip_8.reg[x] = nn
    elif op == 0x7:
        # add
        logging.info(f"add 0x{nn:02X} to 0x{chip_8.reg[x]:02X}, ")
        cycle = 0
        chip_8.reg[x] = (chip_8.reg[x] + nn) % 0x100
        logging.info(f"sum is now 0x{chip_8.reg[x]:02X}\n")
    elif op == 0x8:
        # logic
        cycle = 0
        if n == 0x0:
            # set
            logging.info(f"v{x:X} is now set to the value in v{y:X}\n")
            chip_8.reg[x] = chip_8.reg[y]
        elif n == 0x1:
            # or
            chip_8.reg[x] = chip_8.reg[x] | chip_8.reg[y]
        elif n == 0x2:
            # and
            chip_8.reg[x] = chip_8.reg[x] & chip_8.reg[y]
        elif n == 0x3:
            # xor
            chip_8.reg[x] = chip_8.reg[x] ^ chip_8.reg[y]
        elif n == 0x4:
            # add
            chip_8.reg[x] += chip_8.reg[y]
            if chip_8.reg[x] > 0xFF:
                chip_8.reg[x] %= 0x100
                chip_8.reg[0xF] = 1
            else:
                chip_8.reg[0xF] = 0
        elif n == 0x5:
            # subtract
            chip_8.reg[x] -= chip_8.reg[y]
            if chip_8.reg[x] < 0:
                chip_8.reg[x] += 0x100
                chip_8.reg[0xF] = 0
            else:
                chip_8.reg[0xF] = 1
        elif n == 0x7:
            # subtract other way
            chip_8.reg[x] = chip_8.reg[y] - chip_8.reg[x]
            if chip_8.reg[x] < 0:
                chip_8.reg[x] += 0x100
                chip_8.reg[0xF] = 0
            else:
                chip_8.reg[0xF] = 1
        elif n == 0x6:
            # shift right
            if orig:
                chip_8.reg[x] = chip_8.reg[y]
            logging.info(f"shift v{x:X} = 0x{chip_8.reg[x]:02X} right\n")
            chip_8.reg[0xF] = chip_8.reg[x] & 0x1
            chip_8.reg[x] = chip_8.reg[x] >> 1
            logging.info(f"v{x:X} is now 0x{chip_8.reg[x]:02X}\n")
        elif n == 0xE:
            # shift left
            if orig:
                chip_8.reg[x] = chip_8.reg[y]
            logging.info(f"shift v{x:X} = 0x{chip_8.reg[x]:02X} left\n")
            chip_8.reg[0xF] = chip_8.reg[x] >> 7
            chip_8.reg[x] = chip_8.reg[x] << 1
            chip_8.reg[x] = chip_8.reg[x] & 0xFF
            logging.info(f"v{x:X} is now 0x{chip_8.reg[x]:02X}\n")
    elif op == 0xA:
        # set index
        logging.info(f"set index to 0x{nnn:03X} which points to 0x{chip_8.memory[nnn]:02X}\n")
        cycle = .000055
        chip_8.index = nnn
    elif op == 0xB:
        # offset jump
        logging.info(f"jump to {nnn:03X} + {chip_8.reg[0]:02X}\n")
        cycle = .000105
        if orig:
            chip_8.pc = nnn + chip_8.reg[0]
        else:
            chip_8.pc = nnn + chip_8.reg[x]
    elif op == 0xC:
        # random
        logging.info(f"make v{x:01X} a random number &ed with 0x{nn:02X}\n")
        cycle = .000164
        r = randint(0, nn)
        chip_8.reg[x] = r & nn
    elif op == 0xD:
        # display
        logging.info(f"display instruction at ({chip_8.reg[x]:02X},{chip_8.reg[y]:02X}) that is {n} rows tall\n")
        cycle = 0
        dx = chip_8.reg[x] % 0x40
        dy = 0x1F - chip_8.reg[y] % 0x20
        chip_8.reg[0xF] = 0
        for i in range(n):
            if dy - i < 0:
                break
            if dy - i > 0x20:
                break
            membyt = chip_8.memory[chip_8.index + i]
            for j in range(0x8):
                if dx + j > 0x3F:
                    break
                dispbit = (chip_8.display[dy - i] >> (0x3F - dx - j)) & 0x1
                membit = (membyt >> (0x7 - j)) & 0x1
                if membit == 1:
                    chip_8.display[dy - i] = chip_8.display[dy - i] ^ (0x1 << (0x3F - dx - j))
                    if dispbit == 1:
                        for item in win.items[:]:
                            first_point, second_point = literal_eval(re.split(r"\(|\)", str(item))[2]), literal_eval(re.split(r"\(|\)", str(item))[4])
                            if int(first_point[0]) == dx + j and int(first_point[1]) == dy - i:
                                item.undraw()
                                break
                        chip_8.reg[0xF] = 1
                    else:
                        rect = Rectangle(Point(dx + j, dy - i), Point(dx + j + 1, dy - i + 1))
                        rect.setFill("black")
                        rect.draw(win)
        win.update()
    elif op == 0xE and nn == 0x9E:
        # skip if key is pressed
        cycle = .000073
        ind = chip_8.corr.index(chip_8.reg[x])
        logging.info(f"skip if \"{chip_8.keys[ind]}\" is pressed\n")
        if keyboard.is_pressed(chip_8.keys[ind]):
            logging.info(f"\"{chip_8.keys[ind]}\" is indeed pressed\n")
            chip_8.pc += 2
    elif op == 0xE and nn == 0xA1:
        # skip if key is not pressed
        cycle = .000073
        ind = chip_8.corr.index(chip_8.reg[x])
        logging.info(f"skip if \"{chip_8.keys[ind]}\" is not pressed\n")
        if not keyboard.is_pressed(chip_8.keys[ind]):
            logging.info(f"\"{chip_8.keys[ind]}\" is indeed not pressed\n")
            chip_8.pc += 2
    elif op == 0xF:
        # various instructions
        if nn == 0x07:
            # this and two next are timers
            logging.info(f"v{x:01X} is now 0x{chip_8.reg[x]:03X} from delay\n")
            cycle = .000045
            chip_8.reg[x] = int(chip_8.delay)
        elif nn == 0x15:
            logging.info(f"delay is now 0x{chip_8.reg[x]:03X} from v{x:01X}\n")
            cycle = .000045
            chip_8.delay = chip_8.reg[x]
        elif nn == 0x18:
            logging.info(f"sound is now 0x{chip_8.reg[x]:03X} from v{x:01X}\n")
            cycle = .000045
            chip_8.sound = chip_8.reg[x]
            sound_thread = threading.Thread(target=beep, args=(chip_8.sound,))
            sound_thread.start()
        elif nn == 0x1E:
            # add to index
            logging.info(f"add v{x:01X} = {chip_8.reg[x]:03X} to index\n")
            cycle = .000086
            chip_8.index += chip_8.reg[x]
            if chip_8.index > 0xFFF:
                chip_8.index %= 0x1000
                chip_8.reg[0xF] = 1
            logging.info(f"index is now {chip_8.index:03X}\n")
        elif nn == 0x0A:
            cycle = 0
            while True:
                k = keyboard.read_key()
                if k not in chip_8.keys:
                    continue
                ind = chip_8.keys.index(k)
                break
            chip_8.reg[x] = chip_8.corr[ind]
            logging.info(f"store 0x{chip_8.reg[x]:03X} in v{x:01X} from \"{chip_8.corr[ind]}\" being pressed\n")
        elif nn == 0x29:
            # font character
            cycle = .000091
            chip_8.index = 0x50 + chip_8.reg[x] * 0x5
            logging.info(f"index is now at the font character \"{chip_8.reg[x]:01X}\"\n")
        elif nn == 0x33:
            # binary-coded decimal conversion
            logging.info(f"put v{x:01X} = {chip_8.reg[x]:02X} into memory[{chip_8.index:03X}], in decimal\n")
            cycle = .000927
            b = chip_8.reg[x]
            chip_8.memory[chip_8.index + 2] = b % 10
            b = b // 10
            chip_8.memory[chip_8.index + 1] = b % 10
            b = b // 10
            chip_8.memory[chip_8.index] = b % 10
        elif nn == 0x55:
            # store memory
            logging.info(f"store registers into memory at memory[{chip_8.index:03X}] up to v{x:01X}\n")
            cycle = .000605
            if inc:
                for i in range(x + 1):
                    chip_8.memory[chip_8.index] = chip_8.reg[i]
                    chip_8.index += 1
            else:
                for i in range(x + 1):
                    chip_8.memory[chip_8.index + i] = chip_8.reg[i]
        elif nn == 0x65:
            # load memory
            logging.info(f"load registers from memory from memory[{chip_8.index:03X}] up to v{x:01X}\n")
            cycle = .000605
            if inc:
                for i in range(x + 1):
                    chip_8.reg[i] = chip_8.memory[chip_8.index]
                    chip_8.index += 1
            else:
                for i in range(x + 1):
                    chip_8.reg[i] = chip_8.memory[chip_8.index + i]
        else:
            # unmapped instruction
            break
    cycle /= 60
    if cycle > 0:
        sleep(cycle)
    chip_8.delay -= (time() - tick) * 60
    if chip_8.delay < 0:
        chip_8.delay = 0
win.getMouse()