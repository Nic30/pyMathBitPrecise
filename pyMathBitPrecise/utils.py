from itertools import zip_longest


def grouper(n, iterable, padvalue=None):
    """grouper(3, 'abcdefg', 'x') -->
       ('a','b','c'), ('d','e','f'), ('g','x','x')
    """
    return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)
