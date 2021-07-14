# CHIP-8 Emulator

## What is the CHIP-8?
The CHIP-8 is a virtual machine created in the 1970s that was run in systems such as the COSMAC VIP. Several popular games such as Pong and Tetris were ported over to the CHIP-8. More information can be found [here](https://en.wikipedia.org/wiki/CHIP-8).

## Why make a CHIP-8 emulator?
The CHIP-8 is widely considered to be the best system for "baby's first emulator". It has a very simple structure while still requiring that the developer be comfortable with basic computer architecture like memory management instruction interpretation. This was my first crack at writing an emulator, so this was the one that made sense to me.

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

## How can I write a CHIP-8 emulator?
I used [this guide](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/) to write my emulator. It is language-independent and doesn't completely walk you through the process, so it's a good learning tool. For graphics, I used `graphics.py` and the `GraphWin` object in particular, though there are many, many other graphics tools based around Tkinter.

## Future Development
The largest feature not implemented in this emulator is sound. In the future, it's a possibility that I could add this feature.

All of the ROMs I tested in the emulator work besides sound, and there are extra compatibility options for rare ROMs that work differently.

For the most part, I am moving on to a different emulator, most likely the original Gameboy. I will likely need to learn C++ to make that particular emulator efficient, so that will take some time to complete.
