#!/usr/bin/python3

import os
import sys
import shutil

from config import Config
import naive_parser
import makeNameList
import flagconvert
import localisation
import universe
import events
import readConfig

import logToFile


class Converter:
    def __init__(self):
        self.savefile = Config().getSaveData()
        self.parser = Config().getParser()
        self.topNations = Config().getParser().getTopNations()

    def ConvertEverything(self):
        self.makeFolders()
        self.getUniverse()

        self.convertFlags()
        self.convertNameLists()
        self.convertLocalisation()
        self.convertEvents()

    def CopyMod(self):
        createdModPath = Config().getOutputPath()
        finalPath = Config().getFinalPath()
        createdModFile = Config().getOutputModFile()
        finalModFile = Config().getFinalModFile()
        if not finalPath:
            return

        shutil.rmtree(finalPath, True)
        print("Copying '" + createdModPath + "' to '" + finalPath + "'...")
        shutil.copytree(createdModPath, finalPath)
        print("Copying '" + createdModFile + "' to '", finalModFile + "'...")
        shutil.copyfile(createdModFile, finalModFile)

    def makeFolders(self):
        print("Laying out folder structure...")
        converterDir = Config().getConverterDir()
        shutil.rmtree(Config().getOutputPath(), True)
        shutil.copytree(Config().getBaseModPath(), Config().getOutputPath())

    def getUniverse(self):
        print("Creating the universe...")
        self.universe = universe.Universe(Config().getSaveData(), Config().getHoi4Path())
        print("Establishing history...")
        self.universe.Load()

    def convertFlags(self):
        hoi4flagpath = Config().getHoi4Path() + "gfx/flags/"
        topNations = Config().getParser().getTopNations()

        for topNation in topNations:
            print("Creating flag for " + topNation.tag + "...")
            sourceFlagTga = hoi4flagpath + topNation.tag + "_" + topNation.government + ".tga"
            destFlagFolder = "outputMod/flags/convertedflags/"
            flagconvert.CompileFlag(sourceFlagTga, destFlagFolder)

    def convertNameLists(self):
        topNations = Config().getParser().getTopNations()
        for topNation in topNations:
            print("Creating name list for " + topNation.tag + "...")
            destNameListFolder = "outputMod/common/name_lists/"
            makeNameList.MakeNameList(topNation.tag, Config().getHoi4Path(), destNameListFolder)

    def convertLocalisation(self):
        print("Converting localisation...")

        savefile = Config().getSaveData()
        parser = Config().getParser()
        hoi4path = Config().getHoi4Path()

        localiser = localisation.Localisation(savefile, hoi4path, parser, self.universe)
        print("Writing localisation...")
        localiser.writeLocalisation()
        localiser.writeSyncedLocalisation()

    def convertEvents(self):
        print("Creating events...")

        savefile = Config().getSaveData()
        parser = Config().getParser()
        hoi4path = Config().getHoi4Path()

        self.events = events.Events(savefile, hoi4path, parser, self.universe)
        self.events.makeEvents()


if __name__ == "__main__":
    print("BEGINNING CONVERSION")

    converter = Converter()
    converter.ConvertEverything()
    converter.CopyMod()

    print("ALL DONE!")
