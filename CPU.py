"""CPU Simulator

Written by Michael Crenshaw <mcrenshaw10@liberty.edu> for Honors Petition Credit
in CSIS 434-001, Spring 2016.

CPUsim simulates the operations of a very simple CPU.
Copyright (C) 2016 Michael Crenshaw

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You can read the whole license in the COPYING file.

Registers:
 * AC - accumulator, stores intermediate steps of math operations
 * ECX - loop register, stores number of iterations remaining
 * PC - program counter, stores memory location of current instruction
 * IR - instruction register, stores contents of current instruction

Data storage:
 * Program storage
   Programs are stored as a list of bit strings
 * Data storage
   Data is stored as a list of integers (for convenience)
 * Obviously, these would be combined memory in a real PC. This implementation
   was just far more simple than dealing with start/end registers to delimit
   code and data storage.

Instruction format:
 * Instructions are stored as <opcode><operand1><operand2>. Opcodes are four
   bits, and operands are sixteen each.
 * Available operations are MOV, ADD, SUB, MUL, DIV, and JUMP
 * An operation > opcode table is available in the Compiler module.

Limitations:
 * Cannot handle negative numbers. Makes sense because the programming language
   does not allow direct instantiation of negative numbers. Subtract operations
   will behave incorrectly when operand2 > operand1.
 * Can only handle constants < 32768. Higher numbers are references to variables
   or registers.

Usage:
 * Usage instructions for this program are included in README.
"""

import os

from Compiler import Compiler


class CPU:
    """Simulates a CPU operating on the bytecode defined by the Compiler
       module.
    """

    def __init__(self, code, debug=False):
        """Load a program and prepare to run it. The debug flag enables writing
           output to files for examination.
        """
        self.comp = Compiler(code, debug)
        
        # Load program memory with the bytecode.
        self.prog_memory = str(self.comp).split("\n")

        # Create an empty space for data memory.
        self.data_memory = []

        # Initialize registers.
        self.ac = 0   # Accumulator
        self.ecx = 0  # Loop count
        self.pc = 0   # Program counter
        self.ir = 0   # Instruction register

        # Set debug flag for this instance.
        self.debug = debug

    def __str__(self):
        """Returns string representation of the CPU, i.e. the register
           values.
        """
        return "### REGISTERS ###\n" + \
               "AC =  " + str(self.ac) + "\n" + \
               "ECX = " + str(self.ecx) + "\n" + \
               "PC =  " + str(self.pc) + "\n" + \
               "IR =  " + str(self.ir) + "\n" + \
               "### DATA MEMORY ###\n" + "\n".join([str(x) for x in self.data_memory])
    
    def start(self):
        """Initiates the fetch-execute cycle."""
        while self.pc < len(self.prog_memory):
            print(self)
            self.fetch()
            self.execute()

        if self.debug:
            self.out = open(os.path.join(os.getcwd(), "cpu_output.txt"), "w")
            self.out.write(self.__str__())
            self.out.close()

    def fetch(self):
        """Fetches an instruction from 'memory' and place it in the
           instruction register.
        """
        self.ir = self.prog_memory[self.pc]

    def execute(self):
        """Executes the instruction currently in the instruction register."""
        operation = self.ir[:4]
        operand1 = self.ir[4:20]
        operand2 = self.ir[20:]

        if operation == "0000":
            self.mov(operand1, operand2)
        elif operation == "0001":
            self.add(operand1, operand2)
        elif operation == "0010":
            self.sub(operand1, operand2)
        elif operation == "0011":
            self.mul(operand1, operand2)
        elif operation == "0100":
            self.div(operand1, operand2)
        else:
            if self.ecx > 0:
                self.jump(operand1)
                return  # Skip incrementing 1.

        self.pc += 1

    def mov(self, operand1, operand2):
        """Moves data from operand2 to operand1."""
        ident = int(operand1, 2)

        # If the destination is a variable.
        if ident < 65534:
            index = ident - 32768
            if len(self.data_memory) < index + 1:
                self.data_memory.append(self.get_data(operand2))
            else:
                self.data_memory[index] = self.get_data(operand2)
        # If the destination is the accumulator.
        elif ident == 65534:
            self.ac = self.get_data(operand2)
        # If the destination is the loop register.
        else:
            self.ecx = self.get_data(operand2)

    def add(self, operand1, operand2):
        """Adds data from operand2 to operand1."""
        self.mov(operand1, self.get_data(operand1) + self.get_data(operand2))

    def sub(self, operand1, operand2):
        """Subtracts data in operand2 from operand1."""
        self.mov(operand1, self.get_data(operand1) - self.get_data(operand2))

    def mul(self, operand1, operand2):
        """Multiplies data in operand1 by operand2."""
        self.mov(operand1, self.get_data(operand1) * self.get_data(operand2))

    def div(self, operand1, operand2):
        """Divides data in operand1 by operand2."""
        self.mov(operand1, self.get_data(operand1) / self.get_data(operand2))

    def jump(self, operand):
        """Jumps to the line specified by operand1."""
        self.pc = int(operand, 2)
        
    def get_data(self, operand):
        """Takes a data identifier and determines whether it refers to a
           register or a variable or is simply a constant. Returns the value
           of whichever it is.
        """
        # If the operand hasn't been converted to an int, do so.
        if type(operand) == str:
            ident = int(operand, 2)
        else:
            ident = operand
            
        if ident < 32768:
            return ident
        elif ident < 65534:
            return self.data_memory[ident - 32768]
        elif ident == 65534:
            return self.ac
        else:
            return self.ecx
        
if __name__ == "__main__":
    # Run some test code.
    prog_path = os.path.join(os.getcwd(), "program.dat")
    if os.path.exists(os.path.join(os.getcwd(), "program.dat")):
        with open(prog_path, "r") as prog:
            code = prog.read()
    else:
        code = """x := 17;
                  y := x + 2;
                  z := 0;
                  TO y DO
                      z := z + x
                  END"""
    
    cpu = CPU(code, debug=True)
    cpu.start()
    print(cpu)
