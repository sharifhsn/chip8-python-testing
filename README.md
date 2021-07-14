# CHIP-8 Emulator

## What is the CHIP-8?
The CHIP-8 is a virtual machine that was run in systems such as the COSMAC VIP. Several popular games such as Pong and Tetris were ported over to the CHIP-8. More information can be found [here](https://en.wikipedia.org/wiki/CHIP-8).

## Why make a CHIP-8 emulator?
The CHIP-8 is widely considered to be the best system for "baby's first emulator". It has a very simple structure while still requiring that the developer be comfortable with basic computer architecture like memory managmenet and instruction interpretation. This was my first crack at trying an emulator, so this was the one that made sense to me.

## Why Python?
Python is the language I am most comfortable writing in, so for my first attempt at an emulator I wanted to use it. Python is not commonly used for writing emulators since they are often slow to run; languages like C, C++, and Rust are generally preferred. At the time of this writing, I do not know C++ and Rust, and I am not comfortable coding in C. However, the CHIP-8 is simple enough where Python can be used without causing massive performance issues.

## Instructions for Usage
This emulator can be run by any user, though it currently only has a command line interface.

In the command line, go to the directory `chip8-python-testing` wherever it has been stored in your computer using `cd` commands.

`chip8_unprinted.py` is used to run ROMs, no fancy stuff. `chip8.py` is the same, but has various debugging tools. `ch8_reader` is a debugging tool not intended for the user, it prints various instructions stored in memory. The test ROMs are located in the `programs` directory.

Here is an example command in the terminal that would run Pong:
```
python chip8_unprinted.py programs/PONG
```
