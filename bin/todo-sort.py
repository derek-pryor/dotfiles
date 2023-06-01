import sys
import re

dueDate = re.compile(r"due:(\d{4}-\d{2}-\d{2})")

if __name__ == '__main__':
    lines = {}

    for line in sys.stdin.readlines():
        m = dueDate.search(line)
        if m is None:
            k = None
        else:
            k = m.group(1)

        if k not in lines:
            lines[k] = []

        lines[k].append(line)

    keys = list(lines.keys())
    keys.remove(None)
    keys.sort()
    if None in lines:
        keys.append(None)

    for k in keys:
        lines[k].sort()
        for line in lines[k]:
            print(line, end='', flush=True)
