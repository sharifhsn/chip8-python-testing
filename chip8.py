from graphics import *
import keyboard
import random
import sys
import time
import winsound

# build a chip-8 emulator

# rom name
file_name = sys.argv[1]

# original chip-8, no modification
orig = True
amiga = False
inc = False

# memory - 4096 byte address from 0x000 to 0xFFF
# one byte is two hexademical digits e.g. 0xA9
memory = []
for i in range(0x1000):
    memory.append(0x00)

# initialize font for memory
fonts = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
    0x20, 0x60, 0x20, 0x20, 0x70, # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
    0x90, 0x90, 0xF0, 0x10, 0x10, # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
    0xF0, 0x10, 0x20, 0x40, 0x40, # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90, # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
    0xF0, 0x80, 0x80, 0x80, 0xF0, # C
    0xE0, 0x90, 0x90, 0x90, 0xE0, # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
    0xF0, 0x80, 0xF0, 0x80, 0x80, # F
]
for i in range(len(fonts)):
    memory[0x50 + i] = fonts[i]

# 8-bit registers - sixteen of them, each a byte
reg = []
for i in range(0x10):
    reg.append(0x00)

# 16-bit index register stores memory addresses
index = 0x000

# 16-bit program counter holds next instruction
pc = 0x200

# stack for executing functions (LIFO) 16 levels by default
stk = []

# delay timer, decremented 60 times per second until it reaches 0
delay = 0x00

# sound timer, similar to delay timer, but beeps while not 0
sound = 0x00

# 64 x 32 display pixel memory
# sprites can set and unset display, always xor
# 32 size list of 64 bit rows
display = []
for i in range(0x20):
    display.append(0x0)
win = GraphWin(width = 64 * 16, height = 32 * 16)
win.setCoords(0, 0, 64, 32)

# key implementation
keys = [
    '1', '2', '3', '4',
    'q', 'w', 'e', 'r',
    'a', 's', 'd', 'f',
    'z', 'x', 'c', 'v',
    ]
corr = [
    0x1, 0x2, 0x3, 0xC,
    0x4, 0x5, 0x6, 0xD,
    0x7, 0x8, 0x9, 0xE,
    0xA, 0x0, 0xB, 0xF,
    ]

# clear display
def clear_display(win):
    for i in win.items[:]:
        i.undraw()
    win.update()

# draw display
def draw_display(win, display):
    clear_display(win)
    for i in range(len(display)):
        r = display[i]
        for j in range(0x40):
            dispbit = (r >> (0x3F - j)) & 0x1
            if dispbit == 1:
                rect = Rectangle(Point(j, i), Point(j + 1, i + 1))
                rect.setFill("black")
                rect.draw(win)

# load rom into memory
with open(file_name, mode='rb') as file:
    file_content = file.read()
    for i in range(len(file_content)):
        memory[0x200 + i] = file_content[i]

while True:
    # set cycle speed
    tick = time.time()
    while time.time() <= tick + 1/700:
        pass

    # sound
    if sound > 0:
        winsound.Beep(750, 500)

    # fetch
    instr = (memory[pc] << 8) | memory[pc + 1]
    pc += 2
    
    # nibble information
    op = (instr >> 12) # first nibble
    x = (instr >> 8) & 0xF # second nibble
    y = (instr >> 0x4) & 0xF # third nibble
    n = instr & 0xF # fourth nibble
    nn = instr & 0xFF # second byte (8 bit number)
    nnn = instr & 0xFFF # second nibble plus second byte (12 bit memory address)

    # decode/execute
    if instr == 0x0000:
        # end of program
        break
    elif instr == 0x00E0:
        # clear screen
        for i in range(len(display)):
            display[i] = 0x0000000000000000
        clear_display(win)
    elif instr == 0x00EE:
        # pop stack
        pc = stk.pop()
    elif op == 0x1:
        # jump to nnn
        if pc - 2 == nnn:
            break
        pc = nnn
    elif op == 0x2:
        # call nnn, push current pc to stack
        stk.append(pc)
        pc = nnn
    elif op == 0x3:
        # this and next three are skips
        if reg[x] == nn:
            pc += 2
    elif op == 0x4:
        if reg[x] != nn:
            pc += 2
    elif op == 0x5 and n == 0x0:
        if reg[x] == reg[y]:
            pc += 2
    elif op == 0x9 and n == 0x0:
        if reg[x] != reg[y]:
            pc += 2
    elif op == 0x6:
        # set
        reg[x] = nn
    elif op == 0x7:
        # add
        reg[x] = (reg[x] + nn) % 0x100
    elif op == 0x8:
        # logic
        if n == 0x0:
            # set
            reg[x] = reg[y]
        elif n == 0x1:
            # or
            reg[x] = reg[x] | reg[y]
        elif n == 0x2:
            # and
            reg[x] = reg[x] & reg[y]
        elif n == 0x3:
            # xor
            reg[x] = reg[x] ^ reg[y]
        elif n == 0x4:
            # add
            reg[x] += reg[y]
            if reg[x] > 0xFF:
                reg[x] %= 0x100
                reg[0xF] = 1
            else:
                reg[0xF] = 0
        elif n == 0x5:
            # subtract
            reg[x] -= reg[y]
            if reg[x] < 0:
                reg[x] += 0x100
                reg[0xF] = 0
            else:
                reg[0xF] = 1
        elif n == 0x7:
            # subtract other way
            reg[x] = reg[y] - reg[x]
            if reg[x] < 0:
                reg[x] += 0x100
                reg[0xF] = 0
            else:
                reg[0xF] = 1
        elif n == 0x6:
            # shift right
            if orig:
                reg[x] = reg[y]
            reg[0xF] = reg[x] & 0x1
            reg[x] = reg[x] >> 1
        elif n == 0xE:
            # shift left
            if orig:
                reg[x] = reg[y]
            reg[0xF] = reg[x] >> 7
            reg[x] = reg[x] << 1
            reg[x] = reg[x] & 0xFF
    elif op == 0xA:
        # set index
        index = nnn
    elif op == 0xB:
        # offset jump
        if orig:
            pc = nnn + reg[0]
        else:
            pc = nnn + reg[x]
    elif op == 0xC:
        # random
        r = random.randint(0, nn)
        reg[x] = r & nn
    elif op == 0xD:
        # display
        dx = reg[x] % 0x40
        dy = 0x1F - reg[y] % 0x20
        reg[0xF] = 0
        savx = dx
        for i in range(n):
            if dy - i < 0:
                break
            if dy - i > 0x1F:
                break
            membyt = memory[index + i]
            dx = savx
            for j in range(0x8):
                if dx + j > 0x3F:
                    break
                dispbit = (display[dy - i] >> (0x3F - dx - j)) & 0x1
                membit = (membyt >> (0x7 - j)) & 0x1
                if membit == 1:
                    display[dy - i] = display[dy - i] ^ (0x1 << (0x3F - dx - j))
                    if dispbit == 1:
                        reg[0xF] = 1
        f = memory[index]
        draw_display(win, display)
    elif op == 0xE and nn == 0x9E:
        # skip if key is pressed
        ind = corr.index(reg[x])
        if keyboard.is_pressed(keys[ind]):
            pc += 2
    elif op == 0xE and nn == 0xA1:
        # skip if key is not pressed
        ind = corr.index(reg[x])
        if not keyboard.is_pressed(keys[ind]):
            pc += 2
    elif op == 0xF:
        # various instructions
        if nn == 0x07:
            # this and two next are timers
            reg[x] = int(delay)
        elif nn == 0x15:
            delay = reg[x]
        elif nn == 0x18:
            sound = reg[x]
        elif nn == 0x1E:
            # add to index
            index += reg[x]
            if index > 0xFFF:
                index %= 0x1000
                if amiga:
                    reg[0xF] = 1
        elif nn == 0x0A:
            while True:
                k = keyboard.read_key()
                if k not in keys:
                    continue
                ind = keys.index(k)
                break
            reg[x] = corr[ind]
        elif nn == 0x29:
            # font character
            index = 0x50 + (reg[x] & 0xF) * 0x5
        elif nn == 0x33:
            # binary-coded decimal conversion
            b = reg[x]
            memory[index + 2] = b % 10
            b = int(b / 10)
            memory[index + 1] = b % 10
            b = int(b / 10)
            memory[index] = b % 10
        elif nn == 0x55:
            # store memory
            if inc:
                for i in range(x + 1):
                    memory[index] = reg[i]
                    index += 1
            else:
                for i in range(x + 1):
                    memory[index + i] = reg[i]
            pass
        elif nn == 0x65:
            # load memory
            if inc:
                for i in range(x + 1):
                    reg[i] = memory[index]
                    index += 1
            else:
                for i in range(x + 1):
                    reg[i] = memory[index + i]
        else:
            # incorrect instruction loaded
            exit
    # decrement timers
    delay -= (time.time() - tick) * 60
    if delay < 0:
        delay = 0
    sound -= (time.time() - tick) * 60
    if sound < 0:
        sound = 0
win.getMouse()