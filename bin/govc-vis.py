#!/usr/bin/env python3

import os
import subprocess
import time

import plotext as plt

GOVC_BIN = os.environ.get("GOVC_BIN", "/usr/bin/govc")

def govc(*args):
    result = subprocess.run([GOVC_BIN, *args], capture_output=True)
    return result.stdout.decode()

def where(xs, pattern):
    return [x for x in xs if pattern in x]

def count_lines(output):
    return len(where(output.split("\n"), "stshoot"))

def generate_counts(*args):
    while True:
        yield count_lines(govc(*args))

if __name__ == '__main__':
    counts = 200 # number of data points
    interval = 0 # seconds per count

    xs = range(1, counts + 1)
    ys = []

    plt.title("GOVC Session Count")
    plt.clc()
    plt.xlim(xs[0], xs[-1])
    plt.xticks(ticks=[1,20,40,60,80,100,120,140,160,180,200])

    for y in generate_counts("session.ls"):
        ys.append(y)
        while len(ys) > counts:
            ys.pop(0)
        y_min, y_max = min(ys), max(ys) + 1
        plt.yticks(ticks=range(y_min, y_max))
        plt.ylim(y_min, y_max)
        #plt.ylim(150,165)

        plt.cld()
        plt.clt()
        plt.scatter(xs, ys, marker = "dot")

        plt.sleep(interval)
        plt.show()
