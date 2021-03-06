# CHIP-8 Emulator

## What is the CHIP-8?

The CHIP-8 is a virtual machine created in the 1970s that was run in systems such as the COSMAC VIP. Several popular games such as Pong and Tetris were ported over to the CHIP-8. More information can be found [here](https://en.wikipedia.org/wiki/CHIP-8).

## Why make a CHIP-8 emulator?

The CHIP-8 is widely considered to be the best system for "baby's first emulator". It has a very simple structure while still requiring that the developer be comfortable with basic computer architecture like memory management instruction interpretation. This was my first crack at writing an emulator, so this was the one that made sense to me.

## Why Python?

Python is the language I am most comfortable writing in, so for my first attempt at an emulator I wanted to use it. Python is not commonly used for writing emulators since they are often slow to run; languages like C, C++, and Rust are generally preferred. At the time of this writing, I do not know C++ and Rust, and I am not comfortable coding in C. However, the CHIP-8 is simple enough where Python can be used without causing massive performance issues.

## Instructions for Usage

This emulator can be run by any user, though it currently only has a command line interface. You must have Python 3 installed on your computer.

In the command line, go to the directory `chip8-python-testing` wherever it has been stored in your computer using `cd` commands.

`chip8_interpreter.py` is the main program that is used. `chip8_engine.py` is not used by the user and only provides the emulator object. The first argument must be the filename of the ROM. There are additional optional commands used for rare configurations and debugging:

- `-o` should be used when running ROMs that were not on the original COSMAC VIP
- `-i` should be used when running rare ROMs that are much older on the COSMAC VIP
- `-d` enables debugging mode
- `-l` is used on top of `-d` to pause after every instruction

Here is an example of the most common way to run this program:
```
> python chip8_interpreter.py programs/ibm.ch8
```

The keypad for the original COSMAC VIP looked like this:
![COSMAC VIP keypad](https://github.com/sharifhsn/chip8-python-testing/blob/main/images/cosmac_vip_keypad.png?raw=true)

The implementation on a modern QWERTY keyboard looks like this:
| 1 | 2 | 3 | 4 |
| --- | --- | --- | --- |
| q | w | e | r |
| a | s | d | f |
| z | x | c | v |

## How can I write a CHIP-8 emulator?

I used [this guide](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/) to write my emulator. It is language-independent and doesn't completely walk you through the process, so it's a good learning tool. For graphics, I used `graphics.py` and the `GraphWin` object in particular, though there are many, many other graphics tools based around Tkinter.

## Future Development

I don't currently have any major implementations to add to this emulator.

For the most part, I am moving on to a different emulator, most likely the original Gameboy. I will likely need to learn C++ to make that particular emulator efficient, so that will take some time to complete.
