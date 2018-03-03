#!/usr/bin/python3

import os
import sys
import shutil

import naive_parser
import makeNameList
import flagconvert
import localisation
import universe
import events
import readConfig

import logToFile


class Converter:
    def __init__(self, savefileName, hoi4path):
        self.hoi4path = hoi4path

        self.converterDir = os.path.dirname(os.path.realpath(__file__))
        self.converterDir = self.converterDir.replace("\\", "/") + "/"
        print("Running from: " + self.converterDir)

        print("Parsing save file...")
        self.savefile = naive_parser.ParseSaveFile(savefileName)
        print("Reading save data...")
        self.parser = naive_parser.Parser(self.savefile, self.hoi4path)
        print("Save file parsed.")
        self.topNations = self.parser.getTopNations()

    def ConvertEverything(self):
        self.makeFolders()
        self.getUniverse()

        self.convertFlags()
        self.convertNameLists()
        self.convertLocalisation()
        self.convertEvents()

    def CopyMod(self, targetdir):
        name = "outputMod"
        shutil.rmtree(targetdir + name, True)
        print("Copying '" + self.converterDir + name + "' to '" + targetdir + name + "'...")
        shutil.copytree(self.converterDir + name, targetdir + name)
        print("Copying '" + self.converterDir + name + ".mod' to '", targetdir + name + ".mod'...")
        shutil.copyfile(self.converterDir + name + ".mod", targetdir + name + ".mod")

    def makeFolders(self):
        print("Laying out folder structure...")
        shutil.rmtree(self.converterDir + "outputMod", True)
        shutil.copytree(self.converterDir + "outputMod_base", self.converterDir + "outputMod")

    def getUniverse(self):
        print("Creating the universe...")
        self.universe = universe.Universe(self.savefile, self.hoi4path)
        print("Establishing history...")
        self.universe.Load()

    def convertFlags(self):
        hoi4flagpath = self.hoi4path + "gfx/flags/"

        for topNation in self.topNations:
            print("Creating flag for " + topNation.tag + "...")
            sourceFlagTga = hoi4flagpath + topNation.tag + "_" + topNation.government + ".tga"
            destFlagFolder = "outputMod/flags/convertedflags/"
            flagconvert.CompileFlag(sourceFlagTga, destFlagFolder)

    def convertNameLists(self):
        for topNation in self.topNations:
            print("Creating name list for " + topNation.tag + "...")
            destNameListFolder = "outputMod/common/name_lists/"
            makeNameList.MakeNameList(topNation.tag, self.hoi4path, destNameListFolder)

    def convertLocalisation(self):
        print("Converting localisation...")
        self.localiser = localisation.Localisation(self.savefile, self.hoi4path, self.parser, self.universe)
        print("Writing localisation...")
        self.localiser.writeLocalisation()
        self.localiser.writeSyncedLocalisation()

    def convertEvents(self):
        print("Creating events...")
        self.events = events.Events(self.savefile, self.hoi4path, self.parser, self.universe)
        self.events.makeEvents()


if __name__ == "__main__":
    print("BEGINNING CONVERSION")
    config = readConfig.Config()

    converter = Converter(config.savefile, config.hoi4path)
    converter.ConvertEverything()
    converter.CopyMod(config.targetdir)

    print("ALL DONE!")
