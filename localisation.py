#!/usr/bin/python3

import naive_parser
import getCountryNames
import universe
import sys
import numpy
import codecs
from config import Config


class Localisation:
    def __init__(self, theUniverse):
        self.savefile = Config().getSaveData()
        self.hoi4path = Config().getHoi4Path()
        self.universe = theUniverse
        self.parser = Config().getParser()

        self.localise()

    def localise(self):

        self.empireNames = {}

        countryNames = getCountryNames.getCountryNames()
        for empire in self.universe.empires:
            longtag = empire.longTag()
            empireName = countryNames[longtag]
            empireName = empireName.replace("Empire", "Star Empire")
            if " " not in empireName:
                if empire.government == "communism":
                    govs = [
                        "People's Republic of &",
                        "People's Republic of &",
                        "Socialist Republic",
                        "People's Democratic Republic of &",
                        "Planetary Republic",
                        "Democratic People's Republic",
                        "Republic of &",
                        "Union",
                        "Alliance of ^ Planets",
                        "&",
                        "Space &"]
                elif empire.government == "democratic":
                    govs = [
                        "Republic",
                        "Republic",
                        "Commonwealth",
                        "Union",
                        "United ^ Planets",
                        "Empire",
                        "United Worlds",
                        "Planetary Republic",
                        "Alliance of ^ Planets",
                        "&",
                        "Space &"]
                elif empire.government == "fascism":
                    govs = [
                        "Empire",
                        "Empire",
                        "Greater ^ Empire",
                        "Star Empire",
                        "Imperium",
                        "Hegemony",
                        "&",
                        "Space &",
                        "Planetary Empire"]
                else:
                    govs = [
                        "Empire",
                        "United Worlds",
                        "Planetary Alliance",
                        "Empire of ^ Planets",
                        "Alliance of ^ Planets",
                        "&",
                        "Space &"]

                countryName = empireName
                countryAdj = countryNames[longtag + "_ADJ"]
                empireName = numpy.random.choice(govs)
                if "&" in empireName:
                    empireName = empireName.replace("&", countryName)
                elif "^" in empireName:
                    empireName = empireName.replace("^", countryAdj)
                else:
                    empireName = countryAdj + " " + empireName
            self.empireNames[longtag] = empireName

    def writeLocalisation(self):
        base = open("files/convertertest_l_english.yml", encoding="utf-8").read()
        localisation = base
        for tag in self.empireNames:
            localisation += ' {}:0 "{}"\n'.format(tag, self.empireNames[tag])
        localisation += "\n"

        for tag in self.empireNames:
            localisation += ' NAME_{}:0 "{}"\n'.format(tag, self.empireNames[tag])
        localisation += "\n"

        for tag in self.empireNames:
            smalltag = tag.split("_")[0]
            localisation += ' name_list_{}_names:0 "{}"\n'.format(smalltag, self.empireNames[tag])
        localisation += "\n"

        history = self.universe.GetHistory()
        history = history.replace("\n", "\\n")
        localisation += ' START_SCREEN_CONVERTED:0 "{}"\n\n'.format(history)

        open("outputMod/localisation/convertertest_l_english.yml", "w", encoding="utf-8-sig").write(localisation)

    def writeSyncedLocalisation(self):
        synced = "l_default:\n"
        for tag in self.empireNames:
            synced += ' NAME_{}: "{}"\n'.format(tag, self.empireNames[tag])
        synced += "\n"
        syncedFile = open("outputMod/localisation_synced/converter_names.yml", "w", encoding="utf-8-sig")
        # syncedFile.write(u'\ufeff')
        syncedFile.write(synced)
