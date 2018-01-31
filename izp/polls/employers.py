"""
Employers list
In new file for clearer code.
"""


class Employers:
    """
    Creating list of employers from file
    """

    __list = None

    @classmethod
    def get_list(cls):
        """
        Takes file polls/static/data/employers and converts
           it into the list of employers

        Returns:
            list -- string list of employers
        """
        if cls.__list is None:
            data = []
            try:
                with open("polls/static/data/employers") as f:
                    data = f.read().split('\n')

            except FileNotFoundError:
                print('\033[93m'
                      + "WARNING: File: polls/static/data/employers not found!"
                      + '\n' + '\033[0m')

            cls.__list = data

        return cls.__list
