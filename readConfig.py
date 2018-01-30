#!/usr/bin/python3

import sys
import os.path
import naive_parser

def reformatPath(path, isDir):
    path = path.replace("\\","/")
    if path[0] == '"' and path[-1] == '"':
        path = path[1:-1]

    if isDir and path[-1] != "/":
        path += "/"

    return path

class Config:
    def __init__(self):
        print("Parsing configuration")
        self.configfile = naive_parser.ParseSaveFile("configuration.txt")

        self.savefile = naive_parser.drill(self.configfile, "configuration", "savefile")
        self.hoi4path = naive_parser.drill(self.configfile, "configuration", "HoI4directory")
        self.targetdir = naive_parser.drill(self.configfile, "configuration", "StellarisModdirectory")

        print("Save file: "+self.savefile)
        print("HoI4 location: "+self.hoi4path)
        print("Stellaris mod path: "+self.targetdir)

        self.savefile = reformatPath(self.savefile, False)
        self.hoi4path = reformatPath(self.hoi4path, True)
        self.targetdir = reformatPath(self.targetdir, True)

        if not self.savefile:
            print("Error: Could not parse save file.")
            sys.exit(1)

        if not self.hoi4path:
            print("Error: Could not parse HoI4 path.")
            sys.exit(1)

        if not self.targetdir:
            print("Warning: Could not parse Stellaris mod path. Mod will only be created in the converter directory.")

        for path in [self.savefile, self.hoi4path, self.targetdir]:
            if not os.path.exists(path):
                print("Error: Could not find "+path)
                sys.exit(1)


if __name__ == "__main__":
    config = Config()
    print(config.savefile)
    print(config.hoi4path)
    print(config.targetdir)
