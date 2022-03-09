#!/usr/bin/env python

import argparse
import sys
import re
import fnmatch

class Dependency(object):
    def __init__(self, name_ver):
        self.key = name_ver
        try:
            self.name, self.ver = name_ver.split("@")
        except ValueError:
            self.name = name_ver
            self.ver = ""
        self.deps = []
        self.imports = []

    def add_dep(self, dep):
        self.deps.append(dep)
        dep.imports.append(self)

    def add_import(self, import_):
        self.imports.append(import_)
        import_.deps.append(self)

    def __str__(self):
        return self.key


class Dependencies(object):
    def __init__(self):
        self.deps = {}

    def get(self, key):
        if key not in self.deps:
            self.deps[key] = Dependency(key)
        return self.deps[key]

    def add_link(self, parent, child):
        self.get(parent).add_dep(self.get(child))

    def roots(self):
        return [dep for dep in self.deps.values() if len(dep.imports) == 0]

    def node(self, key):
        if key in self.deps:
            return self.deps[key]
        else:
            return None

    def search(self, query):
        q = re.compile(fnmatch.translate(query))
        return [dep for dep in self.deps.values() if q.match(dep.key)]


def display_tree(dep, field="deps", depth=0, max_depth=None, parents=None):
    if parents is None:
        parents = []

    if depth == 0:
        prefix = ''
    else:
        prefix = '' + ('|   ' * (depth - 1)) + '+-> '

    if dep in parents:
        print(f"{prefix}Circular reference to {dep}")
        return

    print(f"{prefix}{dep}")

    if max_depth is not None and max_depth == depth:
        if len(getattr(dep, field)) > 0:
            print(('|   ' * depth) + '+-> ...')
        return

    parents.append(dep)
    for child in getattr(dep, field):
        display_tree(child, field=field, depth=depth+1, max_depth=max_depth, parents=parents)
    parents.pop()

def display_shortest(dep, field="deps", parents=None, length=None, paths=None):
    if parents is None:
        parents = []
    if paths is None:
        paths = []

    deps = getattr(dep, field)
    if len(deps) == 0:
        if length is None or len(parents) < length:
            length = len(parents)
            paths = [parents[:]]
        elif len(parents) == length:
            paths.append(parents[:])
    else:
        parents.append(dep)
        for child in deps:
            length, paths = display_shortest(child, field=field, parents=parents, length=length, paths=paths)
        parents.pop()

    if len(parents) == 0:
        for path in paths:
            for depth, dep in enumerate(path):
                if depth == 0:
                    print(dep)
                else:
                    print(('   ' * (depth - 1)) + '+-> ' + str(dep))
            print()
    else:
        return length, paths

def parse_input(fh):
  deps = Dependencies()  
  for line in fh.readlines():
    parent, child = line.strip().split(" ")
    deps.add_link(parent, child)
  return deps


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print (and search) the golang mod graph output')
    parser.add_argument("--file", "-f",
                        metavar = "<file>",
                        help = "Read the graph information from a file ('-' for stdin)")
    parser.add_argument("--imports", "-i",
                        const = "imports",
                        default = "deps",
                        action = "store_const",
                        help = "Show the import tree instead of the dependency tree")
    parser.add_argument("--shortest", "-s",
                        action = "store_true",
                        help = "Display the shortest path from the given query to the leaf")
    parser.add_argument("--max-depth", "-d",
                        type = int,
                        help = "The maximum depth of the tree to display")
    parser.add_argument("query",
                        nargs = "?",
                        metavar = "<query>",
                        help = "Glob pattern of the library(s) to show")

    args = parser.parse_args()

    if args.file is None:
        result = subprocess.run(["go", "mod", "graph"], capture_output=True)
        if result.returncode != 0:
            print("Problem running `go mod graph`")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            sys.exit(result.returncode)

        pass
    elif args.file == "-":
        deps = parse_input(sys.stdin)
    else:
        with open(args.file, "r") as fh:
            deps = parse_input(fh)

    if args.query:
        results = deps.search(args.query)
    else:
        results = deps.roots()

    if args.shortest:
        for r in results:
            display_shortest(r, field=args.imports)
    else:
        for r in results:
            display_tree(r, field=args.imports, max_depth=args.max_depth)
            print()
