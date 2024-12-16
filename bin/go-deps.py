#!/usr/bin/env python

import argparse
import sys
import re
import fnmatch
import subprocess
import io
import requests
import requests_cache

requests_cache.install_cache(
        cache_name='go-deps-cache.db',
        backend='sqlite',
        serializer='json',
        expire_after=None,
        allowable_methods=['GET','HEAD'],
        allowable_codes=[200, 404])

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

    def items(self):
        for key in self.deps:
            yield self.deps[key]

    def used_items(self):
        versions = {}
        for key in self.deps:
            name = self.deps[key].name
            ver = self.deps[key].ver

            if name not in versions:
                versions[name] = []

            versions[name].append(ver)

        for name in versions:
            # NOTE: if semver is not used this may not sort correctly
            versions[name].sort()
            ver = versions[name][-1]

            key = name
            if ver != "":
                key = f"{name}@{ver}"

            yield self.deps[key]


def get_pkg_info(name, version):
    url = f"https://pkg.go.dev/{name}"
    if version != "":
        url = f"{url}@{version}"

    resp = requests.get(url)
    if resp.status_code == 404:
        if version != "":
            return get_pkg_info(name, "")
        return "", "", " "
    if resp.status_code != 200:
        raise Exception(f"{resp.status_code} for {url}")

    license = ""
    rslt = re.search("""License: <a (.|\n)*?>(.*?)</a>""", resp.text)
    if rslt is not None:
        license = rslt.group(2)

    repoURL = ""
    rslt = re.search("""<div class="UnitMeta-repo">\n      \n        <a href="(.*?)" """, resp.text)
    if rslt is not None:
        repoURL = rslt.group(1)

    comment = " "
    if ', ' in license:
        comment = license
        license = "Other or more than one license (Please describe in Comments)"
    if license.startswith("BSD"):
        license = "BSD (any variant)"
    elif license == "Apache-2.0":
        license = "Apache 2.0"
    elif license == "ISC":
        license = "ISC (Internet Software Consortium)"

    return license, repoURL, comment


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
        result = subprocess.run(["go", "mod", "graph"], capture_output=True, text=True)
        if result.returncode != 0:
            print("Problem running `go mod graph`")
            print(f"Stdout: {result.stdout}")
            print(f"Stderr: {result.stderr}")
            sys.exit(result.returncode)

        buf = io.StringIO(result.stdout)
        deps = parse_input(buf)
    elif args.file == "-":
        deps = parse_input(sys.stdin)
    else:
        with open(args.file, "r") as fh:
            deps = parse_input(fh)

    for item in deps.used_items():
        if item.name.startswith("gitlab-master.nvidia.com"):
            continue

        name = item.name
        version = item.ver
        license = ""
        licenseURL = ""
        distribution = "Component included in project, not part of a container"
        usage = "Static Linking"
        comments = " "
        locationURL = ""
        internalURL = f"https://urm.nvidia.com/artifactory/sw-workbench-go/{name}/%40v/{version}.zip"

        resp = requests.head(internalURL)
        if resp.status_code != 200:
            print(f"{name} {version} internal url doesn't exist {internalURL}", file=sys.stderr, flush=True)

        license, locationURL, comments = get_pkg_info(name, version)

        proj = ""
        #if item.name.startswith("github.com"):
        #    proj = item.name.lstrip("github.com")
        #elif locationURL.startswith("https://github.com"):
        if locationURL.startswith("https://github.com"):
            #proj = locationURL.lstrip("https://github.com")
            proj = locationURL[18:]
        if proj != "":
            # remove the go version from the URL
            proj = re.split("(/v\d+)$", proj)[0]

            for branch in ["main", "master", "v3", "v1"]: # v3 branch for go-yaml, v1 for go-check
                for filename in ["LICENSE", "LICENSE.txt", "License.txt", "LICENSE.md", "LICENSE.rst", "License", "license", "COPYING"]:
                    url = f"https://raw.githubusercontent.com{proj}/{branch}/{filename}"
                    resp = requests.get(url)
                    if resp.status_code == 200:
                        licenseURL = url
                        break
                if licenseURL != "":
                    break

        if item.name.startswith("golang.org/x"):
            proj = name.lstrip("golang.org")
            licenseURL = f"https://cs.opensource.google/go{proj}+/master:LICENSE"

        if licenseURL == "":
            print(f"{name} {version} license file doesn't exist {locationURL}", file=sys.stderr, flush=True)

        print(f"{name}\t{version}\t{license}\t{licenseURL}\t{distribution}\t{usage}\t{comments}\t{locationURL}\t{internalURL}", flush=True)
