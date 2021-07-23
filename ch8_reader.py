# writes the instructions for a rom in hex
import sys

memory = []
file_name = sys.argv[1]
target = sys.argv[2]
with open(file_name, mode = 'rb') as file:
    file_content = file.read()
    for i in range(len(file_content)):
        memory.append(file_content[i])
instrs = []
for i in range(0, len(memory), 2):
    instr = (memory[i] << 8) | memory[i + 1]
    instrs.append(instr)
rom = ""
for i in range(len(instrs)):
    rom += "0x{:02X}: 0x{:04X}\n".format(i * 2, instrs[i])
with open(target, "w") as f:
    f.write(rom)