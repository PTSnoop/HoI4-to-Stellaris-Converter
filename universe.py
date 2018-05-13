#!/usr/bin/python3

import sys
import os
import math
import naive_parser
import getCountryNames
import properties
import yaml
import numpy
from enum import Enum
from config import Config


class Event:
    def __init__(self, eventType, *tags):
        self.eventType = eventType
        self.tags = tags

    def __str__(self):
        printstring = self.eventType + " "
        for tag in self.tags:
            printstring += tag + " "
        return printstring

    def __eq__(self, other):
        return self.eventType == other.eventType

    def __lt__(self, other):
        return self.eventType < other.eventType


class Empire:
    def __init__(self, nation):
        self.nation = nation
        self.tag = self.nation.tag
        self.score = self.nation.points
        self.population = self.nation.population
        self.industry = self.nation.industry
        self.government = self.nation.government
        self.ideology = self.nation.ideology
        self.climate = self.nation.climate
        self.nuclear = False
        self.colour = "Red"

        self.planetClass = "pc_arid"
        self.penalty = 0
        self.planetSize = 10
        self.planetPopulation = 1
        self.tileBlockers = 8

    def longTag(self):
        return self.tag + "_" + self.government

    def GoIntoSpace(self):
        if self.industry > 0.6:
            self.planetClass = "pc_continental"
        elif self.industry > 0.4:
            if self.climate in ["pc_arid", "pc_desert", "pc_savannah"]:
                self.planetClass = "pc_tropical"
            else:
                self.planetClass = "pc_ocean"
        else:
            self.planetClass = self.climate

        popweight = (self.population + self.population + self.industry) / 3.0
        indweight = (self.population + self.industry + self.industry) / 3.0
        self.planetSize = 10 + math.floor(10 * popweight)
        self.planetPopulation = max(1, math.floor(8 * self.population))
        self.tileBlockers = 10 - (9 * math.floor(indweight))

        if self.score < 0.1:
            self.penalty = 4
        elif self.score < 0.2:
            self.penalty = 3
        elif self.score < 0.4:
            self.penalty = 2
        elif self.score < 0.6:
            self.penalty = 1

    def __str__(self):
        printstring = self.tag + ": "
        printstring += self.planetClass + ". "
        printstring += "Size {}, population {}, {} tile blockers. {}0% penalty.".format(
            self.planetSize, self.planetPopulation, self.tileBlockers, self.penalty)

        return(printstring)


class Universe:
    def __init__(self, savefile):
        self.savefile = savefile
        self.hoi4path = Config().getHoi4Path()
        with open("files/Events.yml") as stream:
            self.eventStrings = yaml.load(stream)

    def Load(self):
        parser = naive_parser.Parser(self.savefile)
        self.topNations = parser.getTopNations()
        self.smallNations = parser.getSmallNations()
        self.gini = parser.getGiniCoeff()
        self.totalScore = parser.getTotalScore()

        self.seed = int(naive_parser.drill(self.savefile, "game_unique_seed"))
        currentDate = naive_parser.drill(self.savefile, "date")
        currentDate = currentDate.replace('"', '')
        self.currentDate = [int(n) for n in currentDate.split(".")]

        self.defcon = Config().defconResults
        if self.defcon:
            self.CreateEventsFromDefcon()
        else:
            self.CreateEvents()

    def CreateEventsFromDefcon(self):
        self.events = []
        climateChange = 0
        self.earthOwnedBy = ""
        self.climateAuthority = ""
        self.earthType = "pc_continental"

        self.empires = []
        for nation in self.topNations:
            self.empires.append(Empire(nation))

        self.nuclearWar = 2

        nuclearTags = []
        for empire in self.empires:
            if empire.tag in self.defcon.keys():
                empire.nuclear = True
                # No need to add population penalties here - the parser's already taken care of that
                nuclearTags.append(empire.tag)

        self.events.append(Event("DefconColdWar"))
        self.events.append(Event("DefconNuclearWar"))

        self.AddClimateEvents()

    def CreateEvents(self):
        self.events = []
        climateChange = 0
        self.nuclearWar = 0
        self.earthOwnedBy = ""
        self.climateAuthority = ""
        self.earthType = "pc_continental"

        self.empires = []
        for nation in self.topNations:
            self.empires.append(Empire(nation))

        if len(self.empires) == 1:
            self.events.append(Event("Hegemon", self.empires[0].tag))
            self.earthOwnedBy = self.empires[0].longTag()
            self.climateAuthority = self.empires[0].tag

        elif self.empires[0].score / self.totalScore > 0.5:  # largest nation has 50%

            if self.empires[1].score / self.empires[0].score > 0.5:  # next largest is pretty big
                self.events.append(Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                self.events.append(Event("MinorNuclearWar", self.empires[0].tag, self.empires[1].tag))
                self.events.append(Event("MinorNuclearWarLose", self.empires[1].tag))
                self.events.append(Event("MinorNuclearWarWin", self.empires[0].tag))

                self.nuclearWar = 1
                self.earthOwnedBy = self.empires[0].longTag()
                self.empires[0].nuclear = True
                self.empires[1].nuclear = True
                self.empires[1].population *= 0.25

            else:  # next largest is pretty small
                self.events.append(Event("EconomicCollapse", self.empires[1].tag))
                self.empires[1].industry *= 0.75
                self.events.append(Event("Hegemon", self.empires[0].tag))
                self.earthOwnedBy = self.empires[0].longTag()

        else:  # largest nation does not have 50%

            if self.empires[0].score / self.totalScore > 0.3:  # someone's large-ish
                if self.empires[1].score / self.empires[0].score > 0.5:  # next largest is pretty big
                    if len(self.empires) == 2:  # only two nations
                        self.events.append(Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                    elif (self.empires[2].score / self.empires[1].score > 0.5):  # and next after that is pretty big too
                        self.events.append(Event("EconomicProblems", self.empires[2].tag))
                        self.empires[2].industry *= 0.9
                        self.events.append(Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                        self.events.append(Event("ColdWarStaysCold", self.empires[0].tag, self.empires[1].tag))
                        self.events.append(Event("Squabbling"))
                    else:  # and next after that is pretty small
                        self.events.append(Event("EconomicCollapse", self.empires[2].tag))
                        self.empires[2].industry *= 0.75
                        self.events.append(Event("ColdWar", self.empires[0].tag, self.empires[1].tag))
                        if self.empires[0].government == self.empires[1].government and self.empires[0].government != "fascist":
                            self.events.append(Event("ColdWarStaysCold", self.empires[0].tag, self.empires[1].tag))
                            self.events.append(Event("Squabbling"))
                        else:
                            self.events.append(Event("NuclearWar", self.empires[0].tag, self.empires[1].tag))
                            self.nuclearWar = 2
                            self.events.append(Event("NuclearWarLose", self.empires[0].tag, self.empires[1].tag))
                            self.empires[0].nuclear = True
                            self.empires[1].nuclear = True
                            self.empires[0].population *= 0.25
                            self.empires[1].population *= 0.25

                else:  # next largest is pretty small
                    self.events.append(Event("EconomicCollapse", self.empires[1].tag))
                    self.empires[1].industry *= 0.75
                    self.events.append(Event("Hegemon", self.empires[0].tag))
                    self.earthOwnedBy = self.empires[0].longTag()

            else:  # everyone's tiny
                self.events.append(Event("Squabbling"))

        self.AddClimateEvents()

    def AddClimateEvents(self):
        if self.gini > 0.4:
            if self.climateAuthority:
                self.events.append(Event("GovernmentClimateControl", climateAuthority))
            elif self.gini > 0.6:
                climateChange = 2
            else:
                climateChange = 1
        else:
            self.events.append(Event("CleanIndustrialization"))

        self.events.append(Event("Migrations"))

        if self.nuclearWar == 2:
            self.events.append(Event("TombWorld"))
            self.events.append(Event("EscapeLaunches"))
            self.earthType = "pc_nuked"
        elif self.nuclearWar == 1:
            if climateChange == 0:
                self.events.append(Event("NuclearWinter"))
                self.events.append(Event("EscapeLaunches"))
                self.earthType = "pc_arctic"
            elif climateChange == 1:
                self.events.append(Event("SeaLevelsRise"))
                self.events.append(Event("Launches"))
                self.earthType = "pc_ocean"
            elif climateChange == 2:
                self.events.append(Event("NuclearIndustrialDesert"))
                self.events.append(Event("EscapeLaunches"))
                self.earthType = "pc_desert"
        else:
            if climateChange == 0:
                self.earthType = "pc_continental"
                self.events.append(Event("Launches"))
                pass
            elif climateChange == 1:
                self.events.append(Event("SeaLevelsRise"))
                self.events.append(Event("Launches"))
                self.earthType = "pc_ocean"
            elif climateChange == 2:
                self.events.append(Event("GlobalWarming"))
                self.events.append(Event("EscapeLaunches"))
                self.earthType = "pc_arid"

        # for event in self.events:
        #    print(event)

        colourMap = properties.getColours()

        for empire in self.empires:

            if empire.tag in colourMap:
                empire.colour = colourMap[empire.tag]

            empire.GoIntoSpace()

        # for empire in self.empires:
        #    print(empire)

    def GetHistory(self):

        tagToName = {}
        tagToAdj = {}
        cityNames = getCountryNames.getCityNames()
        countryNames = getCountryNames.getCountryNames()
        for empire in self.topNations + self.smallNations:
            tagBlank = empire.longTag()
            tagDef = empire.longTag() + "_DEF"
            tagAdj = empire.longTag() + "_ADJ"

            if tagDef in countryNames:
                name = countryNames[tagDef]
            else:
                name = countryNames[tagBlank]
            name = name.replace("The", "the")
            tagToName[empire.tag] = name

            if tagAdj in countryNames:
                adj = countryNames[tagAdj]
            else:
                adj = countryNames[tagBlank]
            tagToAdj[empire.tag] = adj

        numpy.random.seed(self.seed)

        startYear = self.currentDate[0] + 5
        endYear = 2200

        yearRange = endYear - startYear
        eventCount = numpy.random.randint(8, 12)

        nationCount = len(self.topNations) + len(self.smallNations)
        if nationCount == 1:  # only one nation - so events about "nations" won't make much sense
            deleteKeys = []
            for key in self.eventStrings:
                if "nation" in self.eventStrings[key].lower():
                    deleteKeys.append(key)
            for key in deleteKeys:
                del self.eventStrings[key]

        realEvents = []
        for event in self.events:
            if event.eventType in self.eventStrings:
                realEvents.append(Event(event.eventType, *event.tags))

            if event.eventType + "0" in self.eventStrings:
                realEvents.append(Event(event.eventType + "0", *event.tags))

            for i in range(1, 10):
                if event.eventType + str(i) in self.eventStrings and (numpy.random.random() < 0.7):
                    realEvents.append(Event(event.eventType + str(i), *event.tags))

        randomEventCount = eventCount - len(realEvents)

        randomEventKeys = []
        for eventKey in sorted(self.eventStrings):
            if "Random" in eventKey:
                randomEventKeys.append(eventKey)

        randomEvents = []
        skips = 0
        while len(randomEvents) < randomEventCount:
            skips += 1
            if skips > 100:
                break
            chosenEvent = Event(numpy.random.choice(randomEventKeys))
            if chosenEvent not in randomEvents:
                randomEvents.append(chosenEvent)
        randomEvents.sort()

        if randomEventCount > 0:
            jump = eventCount // randomEventCount
            insertPoint = 2 - jump
            if jump == 1:
                insertPoint = 0
            for randomEvent in randomEvents:
                insertPoint += jump
                realEvents.insert(insertPoint, randomEvent)

        # Tried just having linear gaps between years; it doesn't feel right. We
        # need a pretty dense cold-war 20th century and a pretty sparse 22nd
        # century. Log scales to the rescue!
        logNudge = 80
        yearLogScale = numpy.logspace(
            numpy.log10(logNudge), numpy.log10(
                yearRange + logNudge), num=len(realEvents) + 1)

        yearLogScale = [x - logNudge for x in yearLogScale]

        defconResultsText = ""
        if self.defcon:
            def scoreSort(tag):
                try:
                    return self.defcon[tag].score
                except AttributeError:
                    return 0
                    
            survivorTags = []
            okTags = []
            oblitTags = []
            for tag in sorted(self.defcon, key=scoreSort):
                if not type(tag) is str: continue
                survivors = float(naive_parser.drill(self.defcon, tag, "survivors"))
                if survivors > 80:
                    survivorTags.append(tag)
                elif survivors > 40:
                    okTags.append(tag)
                else:
                    oblitTags.append(tag)

            # We've only got 3 "survived" messages and 2 "is basically ok" messages.
            while len(survivorTags) > 3:
                okTags.append(survivorTags.pop())
            while len(okTags) > 2:
                okTags.pop()

            def nameOfTagOrFaction(name):
                if name in tagToName:
                    return tagToName[name]
                return "the "+name.title()
                
            for n in range(len(survivorTags)):
                nationName = "the "+survivorTags[n]
                if survivorTags[n] in tagToName:
                    nationName = tagToName[survivorTags[n]]

                defconResultsText += self.eventStrings["DefconSurvive"+str(n+1)] + " "
                defconResultsText = defconResultsText.replace("&NATION_1&", nameOfTagOrFaction(survivorTags[n]))

            for n in range(len(okTags)):
                defconResultsText += self.eventStrings["DefconOk"+str(n+1)] + " "
                defconResultsText = defconResultsText.replace("&NATION_1&", nameOfTagOrFaction(okTags[n]))

            if len(oblitTags) == 1:
                defconResultsText += self.eventStrings["DefconObliterated1"] + " "
                defconResultsText = defconResultsText.replace("&NATION_1&", nameOfTagOrFaction(oblitTags[0]))
            elif len(oblitTags) > 1:
                for n in range(len(oblitTags)-1):
                    defconResultsText += nameOfTagOrFaction(oblitTags[n]) + ", "
                defconResultsText += "and " + self.eventStrings["DefconObliteratedPl1"]
                defconResultsText = defconResultsText.replace("&NATION_1&", nameOfTagOrFaction(oblitTags[-1]))

        historyString = ""

        for e in range(len(realEvents)):
            year = int(numpy.floor(startYear + yearLogScale[e]))
            yearJump = (yearLogScale[e + 1] - yearLogScale[e]) // 2
            if yearJump > 1:
                year += numpy.random.randint(-yearJump // 2, yearJump // 2)
            if year < startYear:
                year = startYear + 1
            if year > endYear:
                year = endYear - 1
            event = realEvents[e]
            print(event)

            replaces = {}
            replaces["&YEAR&"] = str(year)
            replaces["&DECADE&"] = str(year // 10) + "0s"
            replaces["&NATION_1&"] = tagToName[event.tags[0]] if len(event.tags) > 0 else ""
            replaces["&NATION_2&"] = tagToName[event.tags[1]] if len(event.tags) > 1 else ""
            replaces["&NATION_3&"] = tagToName[event.tags[2]] if len(event.tags) > 2 else ""
            replaces["&NATION_4&"] = tagToName[event.tags[3]] if len(event.tags) > 3 else ""
            replaces["&NATION_5&"] = tagToName[event.tags[4]] if len(event.tags) > 4 else ""
            replaces["&NATION_6&"] = tagToName[event.tags[5]] if len(event.tags) > 5 else ""
            replaces["&NATION_1_ADJ&"] = tagToAdj[event.tags[0]] if len(event.tags) > 0 else ""
            replaces["&NATION_2_ADJ&"] = tagToAdj[event.tags[1]] if len(event.tags) > 1 else ""
            replaces["&NATION_3_ADJ&"] = tagToAdj[event.tags[2]] if len(event.tags) > 2 else ""
            replaces["&NATION_4_ADJ&"] = tagToAdj[event.tags[3]] if len(event.tags) > 3 else ""
            replaces["&NATION_5_ADJ&"] = tagToAdj[event.tags[4]] if len(event.tags) > 4 else ""
            replaces["&NATION_6_ADJ&"] = tagToAdj[event.tags[5]] if len(event.tags) > 5 else ""
            replaces["&DEFCONRESULTS&"] = defconResultsText
            if len(cityNames) > 0:
                replaces["&RANDOM_SMALL_CITY&"] = numpy.random.choice(cityNames)
            else:
                replaces["&RANDOM_SMALL_CITY&"] = "Vienna"

            if len(self.smallNations) > 0:
                replaces["&RANDOM_SMALL_NATION&"] = tagToName[numpy.random.choice(self.smallNations).tag]
            else:
                replaces["&RANDOM_SMALL_NATION&"] = "Secret Denmark"

            eventline = self.eventStrings[event.eventType]
            for replaceString in replaces:
                eventline = eventline.replace(replaceString, replaces[replaceString])
            historyString += eventline + "\n"

        historyString = historyString.replace(". the", ". The")
        historyString = historyString.replace(": the", ": The")

        print(historyString)
        return historyString

    def getEarthTypeFlag(self):
        if self.nuclearWar == 2:
            return "nuclear_war"
        elif self.earthOwnedBy:
            return "give_planet"
        else:
            return "un_bureaucracy"

    def getEarthOwner(self):
        return self.earthOwnedBy

    def getEarthClass(self):
        return self.earthType

    def getEarthEntity(self):
        if self.earthType == "pc_desert":
            return "variable_earth_desert_entity"
        if self.earthType == "pc_arid":
            return "variable_earth_arid_entity"
        if self.earthType == "pc_savannah":
            return "variable_earth_savannah_entity"
        if self.earthType == "pc_tropical":
            return "variable_earth_tropical_entity"
        if self.earthType == "pc_ocean":
            return "variable_earth_ocean_entity"
        if self.earthType == "pc_tundra":
            return "variable_earth_tundra_entity"
        if self.earthType == "pc_arctic":
            return "variable_earth_arctic_entity"
        if self.earthType == "pc_alpine":
            return "variable_earth_alpine_entity"
        if self.earthType == "pc_nuked":
            return "nuked_planet"
        return "continental_planet_earth_entity"

    def getEmpires(self):
        return self.empires


if __name__ == "__main__":
    savefile = naive_parser.ParseSaveFile("postwar_1948_06_16_01.hoi4")

    universe = Universe(savefile)
    universe.Load()

    for empire in universe.getEmpires():
        print(empire)
