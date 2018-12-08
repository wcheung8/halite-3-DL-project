#!/usr/bin/env python3

import os
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from MLBot import *

class NN_Bot(MLBot):
    def __init__(self):
        super().__init__(sys.argv[1]+".nn")


if __name__ == '__main__':
    bot = NN_Bot()
    bot.run()
