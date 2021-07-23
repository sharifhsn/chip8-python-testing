# build a chip-8 emulator
class Chip8():
    def __init__(self) -> None:
        # initialize memory
        self.memory = []
        for i in range(0x1000):
            self.memory.append(0x00)
        
        # add fonts to memory
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
            self.memory[0x50 + i] = fonts[i]
        
        # initialize general registers
        self.reg = []
        for i in range(0x10):
            self.reg.append(0x00)
        
        # 16-bit index register stores memory addresses
        self.index = 0x000

        # 16-bit program counter holds next instruction
        self.pc = 0x200

        # stack for executing functions (LIFO) 16 levels by default
        self.stk = []

        # delay timer, decremented 60 times per second until it reaches 0
        self.delay = 0x00

        # sound timer, similar to delay timer, but beeps while not 0
        self.sound = 0x00

        # 64 x 32 display pixel memory
        self.display = []
        for i in range(0x20):
            self.display.append(0x0)

        # key implementation
        self.keys = [
            '1', '2', '3', '4',
            'q', 'w', 'e', 'r',
            'a', 's', 'd', 'f',
            'z', 'x', 'c', 'v',
            ]
        self.corr = [
            0x1, 0x2, 0x3, 0xC,
            0x4, 0x5, 0x6, 0xD,
            0x7, 0x8, 0x9, 0xE,
            0xA, 0x0, 0xB, 0xF,
            ]