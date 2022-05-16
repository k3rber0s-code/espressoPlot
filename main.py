# data mining
from matplotlib import pyplot as plt
import numpy as np
import os
from itertools import cycle

# Folder Path
path = "."
os.chdir(path)

# Labels
labels = ["0.7", "1.4", "2.8"]

# Colors
cycol = cycle('bgrcmk')

lines =[]

def read_text_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        return lines

timesteps = []
pressures = []


def one_plot():
    timesteps = []
    pressures = []

    for file in os.listdir():
        if file.endswith(".txt"):
            file_path = f"{path}/{file}"
            lines = read_text_file(file_path)
            for line in lines:
                tokens = line.split(",")
                token = tokens[4].split("\n")[0]
                timesteps.append(tokens[0])
                pressures.append(token)
            print(pressures)
            plt.plot(timesteps, pressures, next(cycol))
            timesteps.clear()
            pressures.clear()
    return timesteps, pressures


def subplots(x, y):
    timesteps = []
    pressures = []
    indexes = []

    for i in range(x):
        for j in range(y):
            indexes.append([i, j])
    print(indexes)
    figure, axis = plt.subplots(x, y)
    n = 0

    for file in os.listdir():
        if file.endswith(".txt"):
            file_path = f"{path}/{file}"
            lines = read_text_file(file_path)
            for line in lines:
                tokens = line.split(",")
                token = tokens[4].split("\n")[0]
                timesteps.append(tokens[0])
                pressures.append(token)

            axis[indexes[n][0], indexes[n][1]].plot(timesteps, pressures)
            #axis[0, 0].set_title("Sine Function")
            #plt.plot(timesteps, pressures, next(cycol))
            timesteps.clear()
            pressures.clear()

            n+=1
            if n == len(indexes):
                break

    plt.show()

subplots(2,2)



#plotting
# plt.title('pressure simulation')
# plt.legend(labels)
# plt.xlabel('time')
# plt.ylabel('pressure')
# plt.show()