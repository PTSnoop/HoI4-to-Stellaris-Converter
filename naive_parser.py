#!/usr/bin/python3

import sys
import os
import numpy
import re
from collections import defaultdict

import properties


class Nation:
    def __init__(self, tag):
        self.tag = tag
        self.government = ""
        self.ideology = ""
        self.population = 0.0
        self.industry = 0.0
        self.warscore = 0.0
        self.points = 0.0
        self.name = ""
        self.capital = ""
        self.climate = "pc_arid"

    def longTag(self):
        return self.tag + "_" + self.government

    def __str__(self):
        printstring = ""
        printstring += self.tag + "\n"
        printstring += "\t" + self.government + " " + self.ideology + "\n"
        printstring += "\tPopulation: {:.3f}".format(self.population) + "\n"
        printstring += "\tIndustry: {:.3f}".format(self.industry) + "\n"
        printstring += "\tWarscore: {:.3f}".format(self.warscore) + "\n"
        printstring += "\tOverall: {:.3f}".format(self.points) + "\n"
        return printstring


def drill(blob, *args):
    try:
        thing = blob
        for arg in args:
            thing = thing[arg][0]
        return thing
    except BaseException:
        return ""


def unquote(string):
    if string == "":
        return ""
    string = trim(string)
    if string[0] == '"':
        string = string[1:]
    if string[-1] == '"':
        string = string[:-1]
    return string


def trim(string):
    if string == "":
        return ""
    while string[0] == ' ' or string[0] == '\t':
        string = string[1:]
        if string == "":
            return ""
    while string[-1] == ' ' or string[-1] == '\t':
        string = string[:-1]
        if string == "":
            return ""
    return string


def printstack(stack):
    for blob in stack:
        for line in blob:
            print(line)
        print("-")
    print("---")


def splitstrings(string):
    splits = string.split(",")
    splits = [unquote(s) for s in splits]
    return splits


def ParseSaveFile(path, debug=False):
    try:
        alllines = open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        import traceback
        traceback.print_exc()
        print("Carrying on regardless.")
        alllines = open(path, encoding="utf-8", errors="ignore").read()

    return ParseSaveData(alllines, debug)


def ParseSaveData(alllines, debug=False):

    # Comments are troublesome
    # alllines = re.sub(r"#[^\n]*?\n",r"\n",alllines)

    alllines = re.sub(r"=\n\t*{", r"={", alllines)
    alllines = re.sub(r"=\n *{", r"={", alllines)

    lines = alllines.split("\n")
    lines = [item for item in lines if len(trim(item)) > 0 and trim(item)[0] != "#"]
    alllines = "\n".join(lines)

    alllines = alllines.replace("}", "\n}\n").replace("{", "{\n")
    lines = alllines.split("\n")

    stack = [defaultdict(list)]
    keystack = [""]

    i = 0

    fivePercentMark = len(lines) // 20
    nextPercentMark = fivePercentMark

    if fivePercentMark > 1000:
        print("Parsing save data...")

    for line in lines:
        i += 1

        if i > nextPercentMark and fivePercentMark > 1000:
            print(str((5 * i) // fivePercentMark) + "%")
            nextPercentMark += fivePercentMark

        line = trim(line.replace("\n", "").replace("\t", ""))

        if i == 1:
            # First line weirdness
            if line[:7] == "HOI4bin":
                print("ERROR: The HoI4 save file is compressed, and cannot be read. Please edit 'Documents/Paradox Interactive/Hearst of Iron IV/settings.txt' with a text editor, and change 'save_as_binary=yes' to 'save_as_binary=no'. Then save your HoI4 game again.")
                print("Exiting.")
                sys.exit(0)
            if line == "HOI4txt":
                continue
            if len(line) > 0:
                if ord(line[0]) == 65279:
                    line = line[1:]

        if debug:
            print(line)
            print(stack)
            print(keystack)
            print("")
            input()

        if line == "":
            continue

        end = False
        if '}' in line:
            line = trim(line.replace("}", ""))
            end = True

        if line != "":
            pair = line.split('=')
            key = trim(pair[0])
            if len(pair) > 1:
                value = trim(pair[1])
            else:
                key = ''
                value = trim(line)

            if '{' in value:
                keystack.append(key)
                stack.append(defaultdict(list))
            else:
                stack[-1][key].append(value)

        if end:
            stack[-2][keystack[-1]].append(stack[-1])
            stack.pop()
            keystack.pop()

    savefile = stack[0]

    return savefile


class Parser:
    def __init__(self, savefile, hoi4path):
        self.savefile = savefile
        self.hoi4path = hoi4path

        self.pops = {}
        self.factories = {}
        self.warscore = {}

        states = drill(savefile, "states")
        for state in states:
            owner = unquote(drill(savefile, "states", state, "owner"))
            manpower = drill(savefile, "states", state, "manpower_pool", "total")
            if owner in self.pops:
                self.pops[unquote(owner)] += int(manpower)
            else:
                self.pops[unquote(owner)] = int(manpower)

            buildingtypes = drill(savefile, "states", state, "buildings")
            for buildingtype in buildingtypes:
                rawbuildingcount = trim(
                    drill(
                        savefile,
                        "states",
                        state,
                        "buildings",
                        buildingtype,
                        "level",
                        ""))
                if rawbuildingcount == "":
                    continue
                buildingcount = rawbuildingcount.split(" ")
                for building in buildingcount:
                    if owner in self.factories:
                        self.factories[owner] += int(building)
                    else:
                        self.factories[owner] = int(building)

            wars = savefile["previous_peace"]
            for war in wars:
                for winner in drill(war, "winners"):
                    score = int(drill(war, "winners", winner, "original_score"))
                    if winner in self.warscore:
                        self.warscore[unquote(winner)] += int(score)
                    else:
                        self.warscore[unquote(winner)] = int(score)
            for war in wars:
                for loser in drill(war, "losers"):
                    self.warscore[loser] = 0

        for nation in self.pops:
            if nation not in self.warscore:
                self.warscore[nation] = 0

        self.puppets = []

        for country in drill(savefile, "countries"):
            relation1 = drill(savefile, "countries", country, "diplomacy", "active_relations")
            for relation in relation1:
                relationdata = drill(relation1, relation)
                if "puppet" in relationdata:
                    puppetry = drill(relationdata, "puppet")
                    self.puppets.append([unquote(drill(puppetry, "first")),
                                         unquote(drill(puppetry, "second"))])

        for puppetpair in self.puppets:
            overlord = puppetpair[0]
            vassal = puppetpair[1]

            if overlord not in self.pops:
                continue
            if vassal not in self.pops:
                continue
            self.pops[overlord] += 0.25 * self.pops[vassal]
            self.factories[overlord] += 0.25 * self.factories[vassal]
            self.warscore[overlord] += 0.25 * self.warscore[vassal]

            self.pops[vassal] = 0.1 * self.pops[vassal]
            self.factories[vassal] = 0.1 * self.factories[vassal]
            self.warscore[vassal] = 0.1 * self.warscore[vassal]

        capitals = {}
        for country in drill(savefile, "countries"):
            capitalProvince = drill(savefile, "countries", country, "capital")
            capitals[country] = capitalProvince

        governments = {}
        ideologies = {}
        for country in drill(savefile, "countries"):
            rulingParty = drill(savefile, "countries", country, "politics", "ruling_party")
            governments[country] = rulingParty

            ideology = drill(
                savefile,
                "countries",
                country,
                "politics",
                "parties",
                rulingParty,
                "country_leader",
                "ideology")
            ideologies[country] = ideology

        popmax = float(self.pops[max(self.pops, key=self.pops.get)])
        factorymax = float(self.factories[max(self.factories, key=self.factories.get)])
        scoremax = float(self.warscore[max(self.warscore, key=self.warscore.get)])

        if (popmax < 1):
            popmax = 1
        if (factorymax < 1):
            factorymax = 1
        if (scoremax < 1):
            scoremax = 1

        def tweakedsort(a):
            popproportion = float(self.pops[a]) / popmax
            factoryproportion = float(self.factories[a]) / factorymax
            scoreproportion = float(self.warscore[a]) / scoremax
            factor = (popproportion * factoryproportion)
            factor *= 1.0 + (0.2 * scoreproportion)
            return factor

        self.totalScore = 0.0
        for nation in self.factories:
            self.totalScore += tweakedsort(nation)

        climateMap = properties.getClimates(self.hoi4path)

        self.topNations = []
        self.smallNations = []
        for nation in sorted(self.factories, key=tweakedsort, reverse=True):

            ndata = Nation(nation)
            ndata.population = self.pops[nation] / popmax
            ndata.industry = self.factories[nation] / factorymax
            ndata.warscore = self.warscore[nation] / scoremax
            ndata.points = tweakedsort(nation)

            ndata.government = governments[nation]
            ndata.ideology = ideologies[nation]
            ndata.capital = capitals[nation]
            capitalId = int(ndata.capital)
            if capitalId in climateMap:
                ndata.climate = climateMap[int(capitals[nation])]
            else:
                ndata.climate = "pc_arid"

            oldtag = unquote(drill(savefile, "countries", nation, "original_tag"))
            if oldtag:
                ndata.tag = oldtag

            if len(self.topNations) > 6 or tweakedsort(nation) < 0.1:
                self.smallNations.append(ndata)
            else:
                self.topNations.append(ndata)

        def getIndPerCapita(a):
            return 1000 * (self.factories[a] / self.pops[a])

        def gini_coeff(x):
            # requires all values in x to be zero or positive numbers,
            # otherwise results are undefined
            n = len(x)
            s = x.sum()
            r = numpy.argsort(numpy.argsort(-x))  # calculates zero-based ranks
            return 1 - (2.0 * (r * x).sum() + s) / (n * s)

        villageSize = 1000
        giniVillage = []
        maxWealth = 0.0
        for nation in sorted(self.pops):
            if self.pops[nation] / popmax < 0.005:
                continue
            wealth = (self.factories[nation] / factorymax) / (self.pops[nation] / popmax)
            if wealth > maxWealth:
                maxWealth = wealth
            villagerCount = int(numpy.floor(villageSize * self.pops[nation] / popmax))
            for i in range(villagerCount):
                giniVillage.append(wealth)

        giniArray = numpy.array(giniVillage)
        giniArray = giniArray / maxWealth
        giniArray.sort()
        self.gini = gini_coeff(giniArray)

    def getTopNations(self):
        return self.topNations

    def getSmallNations(self):
        return self.smallNations

    def getTotalScore(self):
        return self.totalScore

    def getGiniCoeff(self):
        return self.gini


if __name__ == "__main__":
    savefile = ParseSaveFile("postwar_1948_06_16_01.hoi4")
    parsedfile = Parser(savefile, "D:/Steam/steamapps/common/Hearts of Iron IV/")
    topNations = parsedfile.getTopNations()
    gini = parsedfile.getGiniCoeff()
    for topNation in topNations:
        print(topNation)
    print("Gini Coefficient: " + str(gini))
