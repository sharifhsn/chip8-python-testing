from graphics import *
import keyboard
import random
import sys
import time

# build a chip-8 emulator [all print statements commented out/deleted]

# rom name
file_name = sys.argv[1]

# programmer mode - optional
prog = False
if len(sys.argv) > 2:
    prog = True

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
fonts = [0xF0, 0x90, 0x90, 0x90, 0xF0, 0x20, 0x60, 0x20, 0x20, 0x70, 0xF0, 0x10, 0xF0, 0x80, 0xF0, 0xF0, 0x10, 0xF0, 0x10, 0xF0, 0x90, 0x90, 0xF0, 0x10, 0x10, 0xF0, 0x80, 0xF0, 0x10, 0xF0, 0xF0, 0x80, 0xF0, 0x90, 0xF0, 0xF0, 0x10, 0x20, 0x40, 0x40, 0xF0, 0x90, 0xF0, 0x90, 0xF0, 0xF0, 0x90, 0xF0, 0x10, 0xF0, 0xF0, 0x90, 0xF0, 0x90, 0x90, 0xE0, 0x90, 0xE0, 0x90, 0xE0, 0xF0, 0x80, 0x80, 0x80, 0xF0, 0xE0, 0x90, 0x90, 0x90, 0xE0, 0xF0, 0x80, 0xF0, 0x80, 0xF0, 0xF0, 0x80, 0xF0, 0x80, 0x80]
j = 0x050
for i in range(len(fonts)):
    memory[j] = fonts[i]
    j += 1

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
# for i in range(0x10):
#     stk.append(0x000)

# stack pointer for the index in the stack
stkp = 0x0

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
#win.getMouse()

# key implementation
keys = ['1', '2', '3', '4', 'q', 'w', 'e', 'r', 'a', 's', 'd', 'f', 'z', 'x', 'c', 'v']
corr = [0x1, 0x2, 0x3, 0xC, 0x4, 0x5, 0x6, 0xD, 0x7, 0x8, 0x9, 0xE, 0xA, 0x0, 0xB, 0xF]

# clear display
def clear_display(win):
    for i in win.items[:]:
        i.undraw()
    win.update()

# draw display
def draw_display(win, display):
    #print("drawing display")
    clear_display(win)
    for i in range(len(display)):
        r = display[i]
        for j in range(0x40):
            dispbit = (r >> (0x3F - j)) & 0x1
            if dispbit == 1:
                rect = Rectangle(Point(j, i), Point(j + 1, i + 1))
                rect.setFill("black")
                rect.draw(win)
    #print("end draw")
# #print("drawing 1/4 left display")
# draw_display(win, display)
# for i in range(len(display)):
#     display[i] = 0x0000FFFF0000FFFF
# #print("drawing something")
# draw_display(win, display)
# clear_display(win)
# draw_display(win, display)
# for i in range(len(display)):
#     display[i] = 0x0000999900009999
# win.getMouse()

# print functions for debugging purposes
# def print_memory(memory):
#     # print mem starting at 0x200
#     i = 0x50
#     while True:
#         if memory[i] == 0 and memory[i + 1] == 0:
#             break
#         #print("0x%X" % i + ": 0x%X" % memory[i], end='\t')
#         i += 1


# def print_registers(reg):
#     for i in range(len(reg)):
#         #print("v%X" % i + ": 0x%X" % reg[i], end=' ')
#     #print()

# load rom into memory
with open(file_name, mode='rb') as file:
    file_content = file.read()
    j = 0x200
    for i in range(len(file_content)):
        memory[j] = file_content[i]
        j += 1
    #print_memory(memory)

while True:
    # timers
    tick = time.time()
    while time.time() <= tick + .001:
        pass
    # fetch
    instr = (memory[pc] << 8) | memory[pc + 1]
    #print("0x%X" % pc + ": 0x%X" % instr, end = '\t')
    pc += 2

    # debugging
    #if prog:
        #print_registers(reg)
        #print("index: 0x{:03X} | ".format(index), end='')
        #print("stk: ", end='')
        #for s in stk:
            #print("0x{:03X},".format(s), end=' ')
        #print()
        # for r in display:
        #     #print("0x{:016x}".format(r))
        #input()
    
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
        #print("program is over")
        break
    elif instr == 0x00E0:
        # clear screen
        #print("clear the screen")
        for i in range(len(display)):
            display[i] = 0x0000000000000000
        clear_display(win)
    elif instr == 0x00EE:
        # pop stack
        #print("pop stack")
        pc = stk.pop()
    elif op == 0x1:
        # jump to nnn
        #print("jump to " + "0x%X" % nnn)
        if pc - 2 == nnn:
            #print("program complete")
            break
        pc = nnn
    elif op == 0x2:
        # call nnn, push current pc to stack
        #print("push 0x{:03X} to stack and jump to 0x{:03X}".format(pc, nnn))
        stk.append(pc)
        pc = nnn
    elif op == 0x3:
        # this and next three are skips
        #print("if v{} == 0x{:02X}, then skip".format(x, nn))
        if reg[x] == nn:
            pc += 2
    elif op == 0x4:
        #print("if v{} != 0x{:02X}, then skip".format(x, nn))
        if reg[x] != nn:
            pc += 2
    elif op == 0x5 and n == 0x0:
        #print("if v{} == v{}, then skip".format(x, y))
        if reg[x] == reg[y]:
            pc += 2
    elif op == 0x9 and n == 0x0:
        #print("if v{} != v{}, then skip".format(x, y))
        if reg[x] != reg[y]:
            pc += 2
    elif op == 0x6:
        # set
        #print("set v%X" % x + " to 0x%X" % nn)
        reg[x] = nn
    elif op == 0x7:
        # add
        #print("add 0x%X" % nn + " to 0x%X" % reg[x], end=', ')
        reg[x] = (reg[x] + nn) % 0x100
        #print("sum is now 0x%X" % reg[x])
    elif op == 0x8:
        # logic
        if n == 0x0:
            # set
            #print("v{} is now set to the value in v{}".format(x, y))
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
            #print("shift v{} = 0x{:0X} right".format(x, reg[x]))
            reg[0xF] = reg[x] & 0x1
            reg[x] = reg[x] >> 1
            #print("v{} is now 0x{:0X}".format(x, reg[x]))
        elif n == 0xE:
            # shift left
            if orig:
                reg[x] = reg[y]
            #print("shift v{} = 0x{:0X} left".format(x, reg[x]))
            reg[0xF] = reg[x] >> 7
            reg[x] = reg[x] << 1
            reg[x] = reg[x] & 0xFF
            #print("v{} is now 0x{:0X}".format(x, reg[x]))
    elif op == 0xA:
        # set index
        #print("set index to 0x{:03X} which points to 0x{:02X}".format(nnn, memory[nnn]))
        index = nnn
    elif op == 0xB:
        # offset jump
        #print("jump to {:03X} + {:02X}".format(nnn, reg[0]))
        if orig:
            pc = nnn + reg[0]
        else:
            pc = nnn + reg[x]
    elif op == 0xC:
        # random
        #print("make v{:01X} a random number &ed with {:02X}".format(x, nn))
        r = random.randint(0, nn)
        reg[x] = r & nn
    elif op == 0xD:
        # display
        #print("display instruction")
        dx = reg[x] % 0x40
        dy = 0x20 - reg[y] % 0x20
        reg[0xF] = 0
        ind = index
        savx = dx
        for i in range(n):
            if dy > 0x1F:
                break
            membyt = memory[ind]
            ##print("membyt at index 0x%X" % ind + " is 0x%X" % membyt)
            dx = savx
            for j in range(0x8):
                if dx > 0x3F:
                    break
                dispbit = (display[dy] >> (0x3F - dx)) & 0x1
                membit = (membyt >> (0x7 - j)) & 0x1
                ##print("dispbit is 0x{:01x} and membit is 0x{:01x}".format(dispbit, membit))
                if membit == 1:
                    display[dy] = display[dy] ^ (0x1 << (0x3F - dx))
                    if dispbit == 1:
                        reg[0xF] = 1
                dx += 1
            dy -= 1
            ind += 1
        f = memory[index]
        draw_display(win, display)
    elif op == 0xE and nn == 0x9E:
        # skip if key is pressed
        ind = corr.index(reg[x])
        #print(f"skip if \"{keys[ind]}\" is pressed")
        if keyboard.is_pressed(keys[ind]):
            #print(f"\"{keys[ind]}\" is indeed pressed")
            pc += 2
    elif op == 0xE and nn == 0xA1:
        # skip if key is not pressed
        ind = corr.index(reg[x])
        #print(f"skip if \"{keys[ind]}\" is not pressed")
        if not keyboard.is_pressed(keys[ind]):
            #print(f"\"{keys[ind]}\" is indeed not pressed")
            pc += 2
    elif op == 0xF:
        # various instructions
        if nn == 0x07:
            # this and two next are timers
            #print("v{:01X} is now 0x{:03X} from delay".format(x, reg[x]))
            reg[x] = int(delay)
        elif nn == 0x15:
            #print("delay is now 0x{:03X} from v{:01X}".format(reg[x], x))
            delay = reg[x]
        elif nn == 0x18:
            #print("sound is now 0x{:03X} from v{:01X}".format(reg[x], x))
            sound = reg[x]
        elif nn == 0x1E:
            # add to index
            #print("add v{:01X} = {:03X} to index".format(x, reg[x]))
            index += reg[x]
            if index > 0xFFF:
                index %= 0x1000
                if amiga:
                    reg[0xF] = 1
            #print("index is now {:03X}".format(index))
        elif nn == 0x0A:
            while True:
                k = keyboard.read_key()
                if k not in keys:
                    continue
                ind = keys.index(k)
                break
            reg[x] = corr[ind]
            #print("store 0x{:03X} in v{:01X} from \"{}\" being pressed".format(reg[x], x, corr[ind]))
        elif nn == 0x29:
            # font character
            index = 0x50 + reg[x] * 0x5
            #print("index is now at the font character \"{:01X}\"".format(reg[x]))
        elif nn == 0x33:
            # binary-coded decimal conversion
            #print("put v{:01X} = {} into memory[{:03X}], in decimal".format(x, reg[x], index))
            b = reg[x]
            memory[index + 2] = b % 10
            b = int(b / 10)
            memory[index + 1] = b % 10
            b = int(b / 10)
            memory[index] = b % 10
        elif nn == 0x55:
            # store memory
            #print("store registers into memory at memory[{:03X}] until {:01X}".format(index, x))
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
            #print("load registers from memory from memory[{:03X}] until {:01X}".format(index, x))
            if inc:
                for i in range(x + 1):
                    reg[i] = memory[index]
                    index += 1
            else:
                for i in range(x + 1):
                    reg[i] = memory[index + i]
        else:
            #print("false instruction loaded")
            exit
    delay -= (time.time() - tick) * 60
    if delay < 0:
        delay = 0
    sound -= (time.time() - tick) * 60
    if sound < 0:
        sound = 0
win.getMouse()