"""
Access code generation module.
Used for creating random unique codes
from digits and uppercase letters.
In other modules use the generate_codes function only.
"""

from string import digits, ascii_uppercase
from random import choice

def _create_code(char_base, length):
    """
    Creates a random code of a given length
    by randomly selecting characters from char_base.
    """
    return ''.join(choice(char_base) for _ in range(length))

def generate_codes(number_of_codes, code_length):
    """
    Generates given number of random unique codes
    of a given length. Please be aware that code length
    must be big enough to randomly generate several different codes. 
    """
    char_base = digits + ascii_uppercase
    if number_of_codes > len(char_base) ** code_length / 10:
        raise ValueError("Codes not long enough")

    generated_codes = []
    while len(generated_codes) < number_of_codes:
        new_code = _create_code(char_base, code_length)
        if new_code not in generated_codes:
            generated_codes.append(new_code)        

    return generated_codes
