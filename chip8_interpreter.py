import sys
import os
import re
from time import time, sleep
from random import randint
import keyboard
from winsound import Beep
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

# nullify print statements if not debugging
if not debug:
    sys.stdout = open(os.devnull, 'w')

# load rom into memory
with open(file_name, 'rb') as f:
    file_content = f.read()
    for i in range(len(file_content)):
        chip_8.memory[0x200 + i] = file_content[i]

# create canvas
win = GraphWin(width=64*16, height=32*16, autoflush=False)
win.setCoords(0, 0, 64, 32)

# interpreter loop
while True:
    # cycle timing
    tick = time()
    if lbl:
        input()

    # sound
    if chip_8.sound > 0:
        Beep(750, 500)

    # fetch instruction
    instr = (chip_8.memory[chip_8.pc] << 8) | chip_8.memory[chip_8.pc + 1]
    chip_8.pc += 2
    
    # debugging print statements
    print("0x{:03X}: 0x{:04X}".format(chip_8.pc - 2, instr), end = '\t')
    for i in range(len(chip_8.reg)):
        print("v{:0X}: 0x{:02X}".format(i, chip_8.reg[i]), end=' ')
    print()
    print("stk: ", end='')
    for s in chip_8.stk:
        print("0x{:03X},".format(s), end=' ')
    print()

    # nibble information
    op = (instr >> 0xC) & 0xF # first nibble
    x = (instr >> 0x8) & 0xF # second nibble
    y = (instr >> 0x4) & 0xF # third nibble
    n = instr & 0xF # fourth nibble
    nn = instr & 0xFF # second byte (8 bit number)
    nnn = instr & 0xFFF # second nibble plus second byte (12 bit memory address)

    # decode and execute instruction
    if instr == 0x0000:
        # end of program
        print("program is over")
        break
    elif instr == 0x00E0:
        # clear screen
        print("clear the screen")
        for i in range(len(chip_8.display)):
            chip_8.display[i] = 0x0
        for i in win.items[:]:
            i.undraw()
        win.update()
    elif instr == 0x00EE:
        # pop stack
        print("pop stack")
        chip_8.pc = chip_8.stk.pop()
    elif op == 0x1:
        # jump to nnn
        print(f"jump to 0x{nnn:02X}")
        if chip_8.pc - 2 == nnn:
            # loops on last instruction
            print("program complete")
            break
        chip_8.pc = nnn
    elif op == 0x2:
        # call nnn, push current chip_8.pc to stack
        print("push 0x{:03X} to stack and jump to 0x{:03X}".format(chip_8.pc, nnn))
        chip_8.stk.append(chip_8.pc)
        chip_8.pc = nnn
    elif op == 0x3:
        # this and next three are skips
        print("if v{:0X} == 0x{:02X}, then skip".format(x, nn))
        if chip_8.reg[x] == nn:
            chip_8.pc += 2
    elif op == 0x4:
        print("if v{:0X} != 0x{:02X}, then skip".format(x, nn))
        if chip_8.reg[x] != nn:
            chip_8.pc += 2
    elif op == 0x5 and n == 0x0:
        print("if v{:0X} == v{:0X}, then skip".format(x, y))
        if chip_8.reg[x] == chip_8.reg[y]:
            chip_8.pc += 2
    elif op == 0x9 and n == 0x0:
        print("if v{:0X} != v{:0X}, then skip".format(x, y))
        if chip_8.reg[x] != chip_8.reg[y]:
            chip_8.pc += 2
    elif op == 0x6:
        # set
        print("set v{:0X} to 0x{:02X}".format(x, nn))
        chip_8.reg[x] = nn
    elif op == 0x7:
        # add
        print("add 0x{:02X} to 0x{:02X}".format(nn, chip_8.reg[x]), end=', ')
        chip_8.reg[x] = (chip_8.reg[x] + nn) % 0x100
        print("sum is now 0x{:02X}".format(chip_8.reg[x]))
    elif op == 0x8:
        # logic
        if n == 0x0:
            # set
            print("v{:0X} is now set to the value in v{:0X}".format(x, y))
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
            print("shift v{:0X} = 0x{:02X} right".format(x, chip_8.reg[x]))
            chip_8.reg[0xF] = chip_8.reg[x] & 0x1
            chip_8.reg[x] = chip_8.reg[x] >> 1
            print("v{:0X} is now 0x{:02X}".format(x, chip_8.reg[x]))
        elif n == 0xE:
            # shift left
            if orig:
                chip_8.reg[x] = chip_8.reg[y]
            print("shift v{:0X} = 0x{:02X} left".format(x, chip_8.reg[x]))
            chip_8.reg[0xF] = chip_8.reg[x] >> 7
            chip_8.reg[x] = chip_8.reg[x] << 1
            chip_8.reg[x] = chip_8.reg[x] & 0xFF
            print("v{:0X} is now 0x{:02X}".format(x, chip_8.reg[x]))
    elif op == 0xA:
        # set index
        print("set index to 0x{:03X} which points to 0x{:02X}".format(nnn, chip_8.memory[nnn]))
        chip_8.index = nnn
    elif op == 0xB:
        # offset jump
        print("jump to {:03X} + {:02X}".format(nnn, chip_8.reg[0]))
        if orig:
            chip_8.pc = nnn + chip_8.reg[0]
        else:
            chip_8.pc = nnn + chip_8.reg[x]
    elif op == 0xC:
        # random
        print("make v{:01X} a random number &ed with 0x{:02X}".format(x, nn))
        r = randint(0, nn)
        chip_8.reg[x] = r & nn
    elif op == 0xD:
        # display
        print("display instruction at ({:02X},{:02X}) that is {} rows tall".format(chip_8.reg[x], chip_8.reg[y], n))
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
        ind = chip_8.corr.index(chip_8.reg[x])
        print(f"skip if \"{chip_8.keys[ind]}\" is pressed")
        if keyboard.is_pressed(chip_8.keys[ind]):
            print(f"\"{chip_8.keys[ind]}\" is indeed pressed")
            chip_8.pc += 2
    elif op == 0xE and nn == 0xA1:
        # skip if key is not pressed
        ind = chip_8.corr.index(chip_8.reg[x])
        print(f"skip if \"{chip_8.keys[ind]}\" is not pressed")
        if not keyboard.is_pressed(chip_8.keys[ind]):
            print(f"\"{chip_8.keys[ind]}\" is indeed not pressed")
            chip_8.pc += 2
    elif op == 0xF:
        # various instructions
        if nn == 0x07:
            # this and two next are timers
            print("v{:01X} is now 0x{:03X} from delay".format(x, chip_8.reg[x]))
            chip_8.reg[x] = int(chip_8.delay)
        elif nn == 0x15:
            print("delay is now 0x{:03X} from v{:01X}".format(chip_8.reg[x], x))
            chip_8.delay = chip_8.reg[x]
        elif nn == 0x18:
            print("sound is now 0x{:03X} from v{:01X}".format(chip_8.reg[x], x))
            chip_8.sound = chip_8.reg[x]
        elif nn == 0x1E:
            # add to index
            print("add v{:01X} = {:03X} to index".format(x, chip_8.reg[x]))
            chip_8.index += chip_8.reg[x]
            if chip_8.index > 0xFFF:
                chip_8.index %= 0x1000
                chip_8.reg[0xF] = 1
            print("index is now {:03X}".format(chip_8.index))
        elif nn == 0x0A:
            while True:
                k = keyboard.read_key()
                if k not in chip_8.keys:
                    continue
                ind = chip_8.keys.index(k)
                break
            chip_8.reg[x] = chip_8.corr[ind]
            print("store 0x{:03X} in v{:01X} from \"{}\" being pressed".format(chip_8.reg[x], x, chip_8.corr[ind]))
        elif nn == 0x29:
            # font character
            chip_8.index = 0x50 + chip_8.reg[x] * 0x5
            print("index is now at the font character \"{:01X}\"".format(chip_8.reg[x]))
        elif nn == 0x33:
            # binary-coded decimal conversion
            print("put v{:01X} = {:02X} into memory[{:03X}], in decimal".format(x, chip_8.reg[x], chip_8.index))
            b = chip_8.reg[x]
            chip_8.memory[chip_8.index + 2] = b % 10
            b = b // 10
            chip_8.memory[chip_8.index + 1] = b % 10
            b = b // 10
            chip_8.memory[chip_8.index] = b % 10
        elif nn == 0x55:
            # store memory
            print("store registers into memory at memory[{:03X}] up to v{:01X}".format(chip_8.index, x))
            if inc:
                for i in range(x + 1):
                    chip_8.memory[chip_8.index] = chip_8.reg[i]
                    chip_8.index += 1
            else:
                for i in range(x + 1):
                    chip_8.memory[chip_8.index + i] = chip_8.reg[i]
            pass
        elif nn == 0x65:
            # load memory
            print("load registers from memory from memory[{:03X}] up to v{:01X}".format(chip_8.index, x))
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
    sleep(1/700)
    chip_8.delay -= (time() - tick) * 60
    if chip_8.delay < 0:
        chip_8.delay = 0
    chip_8.sound -= (time() - tick) * 60
    if chip_8.sound < 0:
        chip_8.sound = 0
win.getMouse()