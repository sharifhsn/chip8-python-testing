# prints the instructions for a rom
import sys

memory = []
fileName = sys.argv[1]
with open(fileName, mode = 'rb') as file:
    fileContent = file.read()
    for i in range(len(fileContent)):
        memory.append(fileContent[i])
print(memory)
instrs = []
for i in range(0, len(memory), 2):
    instr = (memory[i] << 8) | memory[i + 1]
    instrs.append(instr)
def print_instrs(instrs):
    for i in range(len(instrs)):
        if instrs[i] >> 8 == 0x0:
            print("0x%X" % (i * 2) + ": 0x00%X" % instrs[i])
        else:
            print("0x%X" % (i * 2) + ": 0x%X" % instrs[i])
print_instrs(instrs)