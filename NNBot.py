#!/usr/bin/env python3

import os

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from MLBot import *

class NN_Bot(MLBot):
    def __init__(self):
        super().__init__("Agent.nn")


if __name__ == '__main__':
    bot = NN_Bot()
    bot.run()
