#!/usr/bin/python

import os,sys
import math
import re
import colorsys

import naive_parser

def colourDistance(hsv1, hsv2):

    hueDistance = min(abs(hsv2[0]-hsv1[0]), 1-abs(hsv2[0]-hsv1[0]));
    satDistance = abs(hsv2[1]-hsv1[1])
    valDistance = abs(hsv2[2]-hsv1[2])

    return math.sqrt(hueDistance*hueDistance + satDistance*satDistance + valDistance*valDistance)

def getColours(hoi4path):
    hoi4ColourData = naive_parser.ParseSaveFile(hoi4path + "common/countries/colors.txt")
    stellarisGreyData = {
        "grey": [0.65, 0.05, 0.35],
        "dark_grey": [0.65, 0.05, 0.22],
        "black": [0.5,0.3,0.05]
    }
    stellarisColourData = {
        "grey": [0.65, 0.05, 0.35],
        "dark_grey": [0.65, 0.05, 0.22],
        "black": [0.5,0.3,0.05],
        "dark_brown": [0.07,0.6,0.23],
        "brown": [0.07,0.6,0.4],
        "beige": [0.1,0.4,0.6],
        "yellow": [0.11,0.8,0.8],
        "light_orange": [0.09,1.0,0.8],
        "orange": [0.06,0.9,0.7],
        "red_orange": [0.01,0.75,0.7],
        "red": [0.0,0.95,0.5],
        "burgundy": [0.95,0.8,0.35],
        "pink": [0.88,0.61,0.5],
        "purple": [0.74, 0.65, 0.61],
        "dark_purple": [0.74,0.71,0.37],
        "indigo": [0.71,0.85,0.5],
        "dark_blue": [0.64,0.85,0.45],
        "blue": [0.64,0.7,0.6],
        "light_blue": [0.6,0.6,0.7],
        "turquoise": [0.49,0.6,0.6],
        "dark_teal": [0.5,0.6,0.3],
        "teal": [0.42,0.6,0.5],
        "light_green": [0.35,0.5,0.60],
        "green": [0.32,0.6,0.40],
        "dark_green": [0.33,0.6,0.27],
    }

    hsvSet = {}
    nameSet = {}
    for tag in hoi4ColourData:
        colour = naive_parser.drill(hoi4ColourData, tag, "color", "")
        rgb = ("." not in colour)
        colour = [float(x) for x in colour.replace("  "," ").split(" ")]

        if rgb:
            colour = list(colorsys.rgb_to_hsv(*colour))
            colour[2] = colour[2]/255

        hsvSet[tag] = colour

        minDist = 9999
        bestColour = "red"

        if colour[1] < 0.2:
            colourData = stellarisGreyData
        else:
            colourData = stellarisColourData

        for stellarisColour in colourData:
            stellarisHsv = colourData[stellarisColour]
            newDist = colourDistance(colour,stellarisHsv)
            if newDist < minDist:
                minDist = newDist
                bestColour = stellarisColour

        nameSet[tag] = bestColour

    return nameSet

def getStates(hoi4path):
    stateMap = {}

    for filename in os.listdir(hoi4path+"history/states/"):
        stateData = open(hoi4path + "history/states/"+filename).read()

        stateData = stateData.replace("=\n{","={")
        stateData = stateData.replace("=\n\t{","={")
        stateData = stateData.replace("=\n\t\t{","={")
        stateData = stateData.replace("=\n\t\t\t{","={")
        stateData = stateData.replace("=\n\t\t\t\t{","={")
        
        stateData = re.sub(r"#[^\n]*?\n",r"\n",stateData)

        state = naive_parser.ParseSaveData(stateData)

        stateId = int(naive_parser.drill(state,"state","id"))
        provinces = naive_parser.drill(state,"state","provinces","").split(" ")


        provinceIds = []
        for province in provinces:
            if not province: continue
            provinceIds.append(int(province))

        for province in provinceIds:
            stateMap[province] = stateId

    return stateMap

def getClimates(hoi4path):

    climateMap = {}
    stateMap = getStates(hoi4path)

    for filename in os.listdir(hoi4path+"map/strategicregions/"):
        climateData = naive_parser.ParseSaveFile(hoi4path + "map/strategicregions/"+filename)
        provinces = naive_parser.drill(climateData,"strategic_region","provinces","").split(" ")
        periods = naive_parser.drill(climateData,"strategic_region","weather")["period"]
        yearTemperatures = []
        yearRain = []
        yearSnow = []
        yearSand = []

        for province in provinces:
            if not province: continue
            provinceId = int(province)
            if provinceId in stateMap:
                if stateMap[provinceId] == 523:
                    print("FOUND")
                    print(filename)

        if len(periods) == 0:
            continue

        for period in periods:
            temperatureRange = naive_parser.drill(period,"temperature","").split(" ")
            maxTemp = temperatureRange[1].replace("\"","")
            minTemp = temperatureRange[0].replace("\"","")
            temperature = float(maxTemp) - float(minTemp)
            yearTemperatures.append(temperature)

            lightRain = naive_parser.drill(period,"rain_light")
            heavyRain = naive_parser.drill(period,"rain_heavy")
            snow = naive_parser.drill(period,"snow")
            blizzard = naive_parser.drill(period,"blizzard")
            sandstorm = naive_parser.drill(period,"sandstorm")

            yearRain.append(float(lightRain) + float(heavyRain)*2)
            yearSnow.append(float(snow) + float(blizzard)*3)
            yearSand.append(float(sandstorm))

        averageTemperature = sum(yearTemperatures) / len(yearTemperatures)
        averageRain = sum(yearRain) / len(yearRain)
        averageSnow = sum(yearSnow) / len(yearSnow)
        averageSand = sum(yearSand) / len(yearSand)

        climate = "pc_arid"
        if averageSand > 0.05:
            climate = "pc_desert"
        elif averageSnow > 0.3:
            climate = "pc_arctic"
        elif averageSnow > 0.1:
            climate = "pc_tundra"
        elif averageTemperature > 10.0:
            climate = "pc_arid"
        elif averageTemperature < 4.7:
            climate = "pc_savanna"
        else:
            climate = "pc_alpine"
        
        for province in provinces:
            if not province: continue
            provinceId = int(province)
            if provinceId in stateMap:
                stateId = stateMap[provinceId]
                climateMap[stateId] = climate

    return climateMap
            

if __name__ == "__main__":
    hoi4path = "D:/Steam/steamapps/common/Hearts of Iron IV/"
    #hoi4path = "D:/Paradox Interactive/Hearts of Iron IV/mod/Vanilla_Uruguay_End/"
    c = getClimates(hoi4path)
    print(c[523])
