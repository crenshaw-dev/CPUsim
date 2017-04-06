"""Lexical Analyser

This module parses a program following the guidelines described in README and
generates a table of tokens to be assembled by the Assembler module.
"""

import os

from TokenCodes import *


# Define character lists for type validation.
numbers = [str(x) for x in range(10)]
lowercase = [chr(x) for x in range(97, 123)]


class InvalidLexemeException(Exception):
    pass


class Lex():
    """Lexical analyser. Represents a piece of code as a list of Lexemes."""
    
    def __init__(self, input, debug=False):
        """Accepts code and parses it into a list of Lexemes."""
        self.lexemes = []
        self.analyze(input)

        # If debugging is enabled, set it up.
        if debug:
            self.out = open(os.path.join(os.getcwd(), "lex_output.txt"), "w")
            self.out.write(str(self))
            self.out.close()
        
    def __str__(self):
        """Return a string representation of the lexemes and their info."""
        return "\n".join([str(x) for x in self.lexemes]) + "\n"
        
    def analyze(self, code):
        """Accepts textual form of code and returns it as a list of Lexemes."""
        # Split the code by whitespace and store each lexeme.
        for item in code.split():
            if item.endswith(";"):
                self.lexemes += [Lexeme(item[:-1]), Lexeme(";")]
            else:
                self.lexemes.append(Lexeme(item))
        
class Lexeme():
    """Represents a lexeme, storing its textual form as well as its Type, per
       the language definition.
    """
    
    def __init__(self, text):
        """Takes the textual form of a lexeme and determines other pertinent
           information to store in the class instance.
        """
        self.text = text
        self.type = determine_type(text)
        
    def __str__(self):
        """Return a string representation of this lexeme and info about it."""
        return "<Lexeme: %s, %s>" % (self.type, self.text)
        

def determine_type(text):
    """Takes the textual form of a lexeme and returns a textual 
       representation of its type.
    """
    # The first five conditionals check 
    if text in ("TO", "DO", "END"):
        return RESERVED_WORD
    elif text == ":=":
        return ASSIGN_OP
    elif text in ("+", "-", "*", "/"):
        return MATH_OP
    elif text == ";":
        return SEMICOLON
    else:
        # Loop through the lexicon text to determine whether it's a valid
        # constant or variable.
        if text[0] in lowercase:
            type = VARIABLE
        elif text[0] in numbers:
            type = CONSTANT
        else:
            raise InvalidLexemeException(
                "%s should start with a number or lowercase letter." % (text)
                )
        for char in text[1:]:
            if char in numbers:
                pass  # Valid in either const or variable.
            elif char in lowercase:
                # If a letter's found in what appeared to be a const, throw an
                # exception. It's not a valid variable or constant.
                if type == CONSTANT:
                    raise InvalidLexemeException
            else:
                # If something other than a number or lowercase letter appears
                # throw an exception. 
                raise InvalidLexemeException
        return type
