# -*- coding: utf-8 -*-
import string
import random


def make_random_letters_and_digit_string(length=15):
    random_chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(random_chars) for _ in range(length))
