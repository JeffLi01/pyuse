import argparse
import json
import logging
import os
import pkgutil
import sys


class Host:
    def __init__(self):
        self.ip = None
        self.username = None
        self.password = None

    @classmethod
    def from_dict(self, d):
        host = Host()
        for k, v in d.items():
            if hasattr(host, k):
                setattr(host, k, v)
        return host

    def __repr__(self):
        return str({"ip": self.ip, "username": self.username, "password": self.password})

    def __eq__(self, other):
        return self.ip == other.ip and self.username == other.username and self.password == other.password


class Sut:
    def __init__(self):
        self.bmc = None
        self.host = None

    @classmethod
    def from_dict(self, d):
        sut = Sut()
        sut.bmc = Host.from_dict(d["bmc"])
        sut.host = Host.from_dict(d["host"])
        return sut

    def __repr__(self):
        return str({"bmc": self.bmc, "host": self.host})

    def __eq__(self, other):
        return self.bmc == other.bmc and self.host == other.host


def load_sut(json_str):
    sut_dict = json.loads(json_str)
    sut = Sut.from_dict(sut_dict)
    return sut


def load_sut_list(json_str):
    suts = []
    suts_dict = json.loads(json_str)
    for sut_dict in suts_dict.values():
        sut = Sut.from_dict(sut_dict)
        suts.append(sut)
    return suts


def load_sut_list_from_file():
    home = os.path.expanduser("~")
    config_path = os.path.join(home, "suts.json")
    with open(config_path) as sut_file:
        suts = load_sut_list(sut_file.read())
    return suts


def load_current_sut_from_file():
    home = os.path.expanduser("~")
    config_path = os.path.join(home, "sut.json")
    with open(config_path) as sut_file:
        sut = load_sut(sut_file.read())
    return sut


def list_suts():
    suts = load_sut_list_from_file()
    current = load_current_sut_from_file()
    for index, sut in enumerate(suts):
        prefix = " "
        if current is not None and current == sut:
            prefix = "*"
        print("{} {:2d}: {}".format(prefix, index, sut))


def update_current_sut(sut):
    home = os.path.expanduser("~")
    config_path = os.path.join(home, "sut.json")
    with open(config_path, "w") as sut_file:
        str_present = str(sut)
        obj = json.loads(str_present.replace("'", '"'))
        json.dump(obj, sut_file, indent=4)


def use_sut(index):
    suts = load_sut_list_from_file()
    if index >= len(suts):
        print("Out of range")
        sys.exit(-1)
    sut = suts[index]
    update_current_sut(sut)
    print(sut)


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(prog="pyuse")
    version = pkgutil.get_data(__package__, "VERSION.txt").decode(encoding="utf-8")
    parser.add_argument ("-v", "--version", action="version", version=version)
    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument('--log-level', help="setting logging level", default='INFO', choices=levels)
    parser.add_argument("index", help="specify which SUT", nargs="?", type=int)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format='%(levelname)s:%(name)s:%(message)s')

    if args.index is None:
        list_suts()
    else:
        use_sut(args.index)


if __name__ == "__main__":
    main()
