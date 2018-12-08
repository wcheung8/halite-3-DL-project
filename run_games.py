import subprocess
import json
from time import time
import numpy as np
import os

type = "width"
xx = [5, 10, 50 ,75,100,250, 500, 1000]

count = 0
scores = []
for x in xx:

    bot = type+str(x)
    print(bot)
    try:
        os.mkdir("replays/" + bot )
    except:
        print("replays already made")
    
    for i in range(10):
        proc_output = subprocess.getoutput('halite.exe --replay-directory replays/'+bot+' --results-as-json --width 32 --height 32 --turn-limit 200 "python MyBot.py '+ type+str(x)+'" "python MyBot.py '+ type+str(x)+'"')
        stats = json.loads(proc_output[proc_output.find('{'):])['stats']['0']
        score = stats['score']
        print(str(i) + "\t" + str(score))
        scores.append(score)