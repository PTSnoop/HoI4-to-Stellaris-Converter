#!/usr/bin/python3

import os,sys
import re
import random
import naive_parser
import unicodedata

def removeAccents(inputNames):
    outputNames = []
    for name in inputNames:
        try:
            nfkd_form = unicodedata.normalize('NFKD', name)
            name = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
            name = name.encode('utf-8').decode('ascii')
            outputNames.append(name)
        except UnicodeEncodeError:
            pass
        except UnicodeDecodeError:
            pass
    return outputNames

def ClunkyStringSplit(string):
    outputs = []
    currentOutput = ""
    quoted = False

    for char in string:
        if char == '"':
            quoted = not quoted
        elif char == " " and not quoted:
            outputs.append(currentOutput)
            currentOutput = ""
        else:
            currentOutput += char

    if currentOutput != "":
        outputs.append(currentOutput)
    return outputs

def stringlist_drill(*args):
    output = []
    theStrings = naive_parser.drill(*args)
    if theStrings:
        for line in theStrings['']:
            output += ClunkyStringSplit(line)
    return output
            
def TemplateFill(data, filename, writefilename):
    for key in data:
        if isinstance(data[key],list):
            newdata = ""
            for entry in data[key]:
                newdata += '"{}" '.format(entry)
            data[key] = newdata

    filedata = open(filename).read()
    for key in data:
        filedata = filedata.replace(key,data[key])

    output = open(writefilename,'w',encoding="utf-8")
    output.write(filedata)

def MakeNameList(tag,hoi4path,destFolder):

    includeGenericUnitNames = True

    namespath = hoi4path + "common/names/01_names.txt";
    if os.path.exists(namespath):
        print("Reading names from modded "+namespath)
        names = naive_parser.ParseSaveFile(namespath)
    else:
        print("Reading names from " +      hoi4path + "common/names/00_names.txt")
        names = naive_parser.ParseSaveFile(hoi4path + "common/names/00_names.txt")

    modUnitNamesPath = hoi4path + "common/units/names/01_names.txt"
    if os.path.exists(modUnitNamesPath):
        print("Reading unit names from modded "+modUnitNamesPath)
        unitnames = naive_parser.ParseSaveFile(modUnitNamesPath)
        includeGenericUnitNames = False
    else:
        specialUnitNamePath = hoi4path + "common/units/names/00_"+tag+"_names.txt"
        if os.path.exists(specialUnitNamePath):
            print("Reading unique unit names from "+specialUnitNamePath)
            unitnames = naive_parser.ParseSaveFile(specialUnitNamePath)
        else:
            print("Could not find "+specialUnitNamePath)
            print("Reading unit names from " +     hoi4path + "common/units/names/00_names.txt")
            unitnames = naive_parser.ParseSaveFile(hoi4path + "common/units/names/00_names.txt")

    malenames = stringlist_drill(names,tag,"male","names")
    femalenames = stringlist_drill(names,tag,"female","names")
    surnames = stringlist_drill(names,tag,"surnames")

    subs = stringlist_drill(unitnames,tag,"submarine","unique")
    destroyers = stringlist_drill(unitnames,tag,"destroyer","unique")
    light_cruisers = stringlist_drill(unitnames,tag,"light_cruiser","unique")
    heavy_cruisers = stringlist_drill(unitnames,tag,"heavy_cruiser","unique")
    battle_cruisers = stringlist_drill(unitnames,tag,"battle_cruiser","unique")
    battleships = stringlist_drill(unitnames,tag,"battleship","unique")
    carriers = stringlist_drill(unitnames,tag,"carrier","unique")

    if includeGenericUnitNames:
        subs += stringlist_drill(unitnames,tag,"submarine","generic")
        destroyers += stringlist_drill(unitnames,tag,"destroyer","generic")
        light_cruisers += stringlist_drill(unitnames,tag,"light_cruiser","generic")
        heavy_cruisers += stringlist_drill(unitnames,tag,"heavy_cruiser","generic")
        battle_cruisers += stringlist_drill(unitnames,tag,"battle_cruiser","generic")
        battleships += stringlist_drill(unitnames,tag,"battleship","generic")
        carriers += stringlist_drill(unitnames,tag,"carrier","generic")

    planetnames = subs
    ships = destroyers + light_cruisers + heavy_cruisers + battle_cruisers + battleships + carriers

    planetnames = [sub for sub in subs if not any(char.isdigit() for char in sub)]

    # Leave this in until I work out what accents Stellaris can't take
    ships = removeAccents(ships)
    planetnames = removeAccents(planetnames)
    malenames = removeAccents(malenames)
    femalenames = removeAccents(femalenames)
    surnames = removeAccents(surnames)

    if len(planetnames) < 20:
        extraplanets = ships[:]
        random.shuffle(extraplanets)
        planetnames += extraplanets

    print(len(planetnames))

    templateData = {}
    templateData["&TAG&"] = tag
    templateData["&SHIPNAMES&"] = ships
    templateData["&PLANETNAMES&"] = planetnames
    templateData["&MALENAMES&"] = malenames
    templateData["&FEMALENAMES&"] = femalenames
    templateData["&SURNAMES&"] = surnames

    TemplateFill(templateData, "files/stellaris_name_list_template.txt", destFolder+tag+"_test.txt")
    
if __name__ == "__main__":
    MakeNameList("FRA")
