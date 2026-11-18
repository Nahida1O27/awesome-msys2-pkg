#!/bin/python3
# it need to be executed in MSYS2 bash and depends on python-requests
# this script is used to update the hash sums in the PKGBUILD file
# get sha256 from GiHub REST API
import os

import requests


class metadata:
    def __init__(self, host: str, ver: str):
        self.host = host
        self.ver = ver
        self.filename = f"clice-{ver}.{host}.zip"


# read info from ./PKGBUILD
def read_info() -> metadata:
    host = os.getenv("MINGW_CHOST")
    ver = ""
    with open("PKGBUILD", "r", encoding="utf-8") as f:
        for line in f:
            if "pkgver=" in line:
                ver = line.split("=")[1].strip()
                break
    return metadata(host, ver)


# curl -L \
# -H "Accept: application/vnd.github+json" \
# "https://api.github.com/repos/clice-io/clice/releases/tags/v1.0.0"
def fetch_json(meta: metadata) -> dict:
    url: str = f"https://api.github.com/repos/clice-io/clice/releases/tags/v{meta.ver}"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers, allow_redirects=True, timeout=30)
    response.raise_for_status()
    return response.json()


def main() -> int:
    json = fetch_json(read_info())
    # find sha256 of read_info().filename in json["assets"]
    sha256 = ""
    for asset in json["assets"]:
        if asset["name"] == read_info().filename:
            sha256 = asset["digest"]
            break
    print(f"filename: {read_info().filename}")
    print(sha256)
    # remove var sha256 prefix: "sha256:"
    sha256 = sha256[7:]
    # write PKGBUILD with new sha256sums
    with open("PKGBUILD", "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open("PKGBUILD", "w", encoding="utf-8") as f:
        for line in lines:
            if "sha256sums=(" in line:
                f.write(f'sha256sums=("{sha256}")\n')
                print("update sha256 in PKGBUILD, from")
                print(line[:-1] + "\\n")
                print("to ⬇️⬇️⬇️⬇️⬇️⬇️")
                print(f'sha256sums=("{sha256}")\\n')
            else:
                f.write(line)
    return 0


if __name__ == "__main__":
    main()
