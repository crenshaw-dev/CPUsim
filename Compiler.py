"""Compiler

This module compiles the simple assembly instructions described below into
bytecode executable by the CPU module.

### Program Storage Format ###
Opcode    Operand1            Operand2
XXXX      XXXXXXXXXXXXXXXX    XXXXXXXXXXXXXXXX

Operands beginning with 1 designate variables or registers. That is, 0 - 65535
are available for constants. Because only two user-accessible registers exist,
32768 - 65533 are available for variables, and 65534 - 65535 are registers.

### Operator Codes ###
MOV    0000    Moves data of second operand into first operand

ADD    0001    Adds data of second operand into first operand
SUB    0010    Subtracts data of second operand from first operand
MUL    0011    Multiplies data of first operand by second operand
DIV    0100    Divides data of first operand by second operand

JMP    0101    Jumps to position of first (only) operand if ECX register == 0

### Register Codes ###
AC     1111111111111110    (65534)
ECX    1111111111111111    (65535)
"""

import os

from Assembler import Assembler


operators = {
    "MOV": "0000",
    "ADD": "0001",
    "SUB": "0010",
    "MUL": "0011",
    "DIV": "0100",
    "JMP": "0101"
}

registers = {
    "AC": "1111111111111110",
    "ECX": "1111111111111111"
}


class Compiler:
    """Reads assembly code as defined by Assembler and converts it to bytecode
       to be executed by the CPU module.
    """

    def __init__(self, code, debug=False):
        """Takes a program, runs it through the assembler, and converts that
           code to bytecode.
        """
        self.variables = {}
        assembly = str(Assembler(code, debug))
        self.bytecode = self.comp(assembly)

        # If debugging is enabled, set it up.
        if debug:
            self.out = open(os.path.join(os.getcwd(), "compiler_output.txt"), "w")
            self.out.write(self.bytecode)
            self.out.close()

    def __str__(self):
        """Returns the string representation of the compiled bytecode."""
        return self.bytecode

    def comp(self, assembly):
        """Takes assembly code and returns bytecode representation."""
        bytecode = ""
        instr_count = 0
        label = 0
        for line in assembly.strip().split("\n"):
            parts = line.split()
            operator = parts[0]

            if operator.startswith("label"):
                label = instr_count
                continue  # i.e. don't increment the instruction counter
            elif operator == "JMP":
                bytecode += operators[operator]

                # Jump to previously-set label. Doesn't matter what the
                # label is, because nested loops aren't allowed.
                bytecode += dec_to_bin(label, 16)

                # Add empty operand.
                bytecode += dec_to_bin(0, 16)
            else:
                # Add operator to the bytecode.
                bytecode += operators[operator]

                # Add operand1 to the bytecode.
                operand1 = parts[1]
                if operand1 in registers.keys():
                    bytecode += registers[operand1]
                else:
                    bytecode += self.variable(operand1)
                    
                # Add operand2 to the bytecode.
                operand2 = parts[2]
                try:
                    # Only works if it's a constant.
                    bytecode += dec_to_bin(int(operand2), 16)
                except:
                    # Must be a variable or register.
                    if operand2 in registers.keys():
                        bytecode += registers[operand2]
                    else:
                        bytecode += self.variable(operand2)

            bytecode += "\n"
            instr_count += 1

        return bytecode.strip()  # Strip removes the trailing newline.

    def variable(self, var):
        """Takes a variable name. If it already has a binary representation,
           return that. Otherwise, assign a binary representation, and return
           it.
        """
        if len(self.variables) == 0:
            self.variables[var] = 2**15
        elif var not in self.variables.keys():
            self.variables[var] = max(self.variables.values()) + 1

        return dec_to_bin(self.variables[var], 16)

def dec_to_bin(decimal, length):
    """Accepts a decimal integer and returns a string representation of the
       equivalent binary. If the binary representaiton is longer than length,
       return the oversized string without resizing.
    """
    string = ""
    while decimal > 0:
        string = str(decimal % 2) + string
        decimal /= 2

    if len(string) < length:
        return ("0" * (length - len(string))) + string
    
    return string
