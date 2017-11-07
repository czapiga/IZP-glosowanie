"""
Random access codes generation module.
To use, import the generate_codes function and call it,
specifying number of codes and length of a single code.
The latter should be around 8-10 characters as a compromise
between safety and users' comfort.

All generated codes have a random part and an unique part.
The unique part is there to ensure that no two codes are the same
and is as short as possible (expected no more than 2 characters
in this project's use cases).
"""

from string import ascii_uppercase, digits
from random import choice
from math import ceil

def _create_code(char_base,
                 random_part_length,
                 unique_part_length,
                 index):
    """
    Private helper function. Do not use in other modules.

    The random part of the code is created from randomly selected characters
    from the character base. The unique part creation can be described
    as converting the index to a base-decimal number system, where base is the
    number of different characters in character base.
    """

    random_part = ''.join(choice(char_base) for _ in range(random_part_length))

    base = len(char_base)
    unique_part = ''
    for exp in range(unique_part_length - 1, -1, -1):
        unique_part += char_base[index // base ** exp]
        index = index % base ** exp

    return random_part + unique_part


def generate_codes(number_of_codes, code_length):
    """
    Public function to be imported.

    Raises ValueError if code length is not big enough to create
    desired number of unique codes. Length of the random part of the
    access code can be 0 (not recommended though).
    """
    char_base = digits + ascii_uppercase
    unique_part_length = ceil(number_of_codes / len(char_base))

    if unique_part_length > code_length:
        raise ValueError("Codes must be at least %d characters long"
                         % unique_part_length)

    codes = []
    for index in range(number_of_codes):
        codes.append(_create_code(char_base,
                                  code_length - unique_part_length,
                                  unique_part_length,
                                  index))
    return codes
