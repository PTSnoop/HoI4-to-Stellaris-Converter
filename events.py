#!/usr/bin/python3

import naive_parser
import universe
import numpy

class Dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Events:
    def __init__(self, savefile, hoi4path, parser, theUniverse):
        self.savefile = savefile
        self.hoi4path = hoi4path
        self.universe = theUniverse
        self.parser = parser

        self.text_start = open("files/converter_events_start.txt").read()
        self.text_planet = open("files/converter_events_planet.txt").read()
        self.text_give_earth = open("files/converter_events_give_earth.txt").read()
        self.text_opinion_penalty = open("files/converter_events_opinionpenalty.txt").read()
        self.text_new_human = open("files/converter_events_newhuman.txt").read()
        self.text_option = open("files/converter_events_option.txt").read()

    def makeEvents(self):
        event = self.text_start

        empires = self.universe.getEmpires()

        self.earthTypeFlag = self.universe.getEarthTypeFlag()
        self.earthOwner = self.universe.getEarthOwner()
        self.earthClass = self.universe.getEarthClass()
        self.earthEntity = self.universe.getEarthEntity()

        if not self.earthOwner: self.earthOwner = "nobody"

        planetsString = ""
        for e in range(len(empires)):
            empire = empires[e]
            planetsString += self.makePlanet(empire, e)

        opinionPenalties = ""
        for judgedEmpire in empires:
            if not judgedEmpire.nuclear: continue
            for opinionatedEmpire in empires:
                newPenalty = self.text_opinion_penalty
                newPenalty = newPenalty.replace("&LONGTAG_OPINIONATED&", opinionatedEmpire.longTag())
                newPenalty = newPenalty.replace("&LONGTAG_JUDGED&", judgedEmpire.longTag())
                opinionPenalties += newPenalty

        optionsString = ""
        for empire in empires:
            option = self.text_option.replace("&LONGTAG&", empire.longTag())
            optionsString += option
        
        event = event.replace("&EARTH_TYPE_FLAG&", self.earthTypeFlag)
        event = event.replace("&EARTH_OWNER_LONGTAG&", self.earthOwner)
        event = event.replace("&EARTH_PC_TYPE&", self.earthClass)
        event = event.replace("&EARTH_ENTITY&", self.earthEntity)
        event = event.replace("&PLANETS&", planetsString)
        event = event.replace("&OPINION_PENALTIES&", opinionPenalties)
        event = event.replace("&OPTIONS&", optionsString)

        open("outputMod/events/converter_events.txt","w").write(event)

    def makePlanet(self, empire, idnumber):
        if idnumber > 6: return ""
        planet = self.text_planet

        '''
            &PLANET_ID& : planet_1_1
            &PLANET_SIZE_DELTA& : -2
            &PLANET_PC_TYPE& : pc_continental
            &OWNER_TAG& : SOV
            &OWNER_LONGTAG& : SOV_communism

            &AUTHORITY& : auth_dictatorial
            &ETHICS& : ethic = "ethic_xenophobe" \n ethic = "ethic_authoritarian" \n ethic = "ethic_materialist"
            &CIVICS& : civic = civic_police_state \n civic = civic_functional_architecture

            &COLOUR& : red
            &MODIFIER& : converted_2_nuclear
            &NEW_HUMANS& : converter_events_newhuman.txt repeated

            &MINERALS& : 1000
            &ENERGY& : 1000
            &FOOD& : 150
            &INFLUENCE& : 500
        '''

        planet_id = "planet_" + str(1+ (idnumber//3)) + "_" + str(1+ (idnumber % 3))
        planet_size_delta = str(empire.planetSize - 16)
        planet_pc_type = empire.planetClass
        owner_tag = empire.tag
        owner_longtag = empire.tag + "_" + empire.government

        government = self.getGovernment(empire)

        colour = empire.colour
        modifier = "converted_"+str(empire.penalty)+"_"
        if empire.nuclear:
            modifier += "nuclear"
        else:
            modifier += empire.government
        humancount = empire.planetPopulation - 3

        minerals = "1000"
        energy = "1000"
        food = "150"
        influence = "500"

        ethicsString = ""
        for ethic in government.ethics:
            ethicsString += 'ethic = "{}"\n'.format(ethic)
        civicsString = ""
        for civic in government.civics:
            civicsString += 'civic = "{}"\n'.format(civic)

        humanString = ""
        for i in range(humancount):
            humanString += self.text_new_human

        planet = planet.replace("&PLANET_ID&",planet_id)
        planet = planet.replace("&PLANET_SIZE_DELTA&",planet_size_delta)
        planet = planet.replace("&PLANET_PC_TYPE&",planet_pc_type)
        planet = planet.replace("&OWNER_TAG&",owner_tag)
        planet = planet.replace("&OWNER_LONGTAG&",owner_longtag)
        planet = planet.replace("&AUTHORITY&",government.authority)
        planet = planet.replace("&ETHICS&",ethicsString)
        planet = planet.replace("&CIVICS&",civicsString)
        planet = planet.replace("&COLOUR&",colour)
        planet = planet.replace("&MODIFIER&",modifier)
        planet = planet.replace("&NEW_HUMANS&",humanString)
        planet = planet.replace("&MINERALS&",minerals)
        planet = planet.replace("&ENERGY&",energy)
        planet = planet.replace("&FOOD&",food)
        planet = planet.replace("&INFLUENCE&",influence)
        
        return planet

    def getGovernment(self, empire):
        government = Dotdict({})

        empire.ideology = empire.ideology.replace("_neutral","")

        if empire.ideology == "conservatism":
            government.authority = "auth_democratic"
            government.ethics = ["ethic_egalitarian","ethic_pacifist","ethic_xenophobe"]
            government.civics = ["civic_parliamentary_system", "civic_environmentalist"]

        elif empire.ideology == "liberalism":
            government.authority = "auth_democratic"
            government.ethics = ["ethic_fanatic_egalitarian","ethic_xenophile"]
            government.civics = ["civic_beacon_of_liberty", "civic_idealistic_foundation"]

        elif empire.ideology == "socialism":
            government.authority = "auth_democratic"
            government.ethics = ["ethic_fanatic_egalitarian","ethic_pacifist"]
            government.civics = ["civic_environmentalist", "civic_meritocracy"]

        ###

        elif empire.ideology == "marxism":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_materialist","ethic_pacifist"]
            government.civics = ["civic_police_state","civic_technocracy"]

        elif empire.ideology == "leninism":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_materialist","ethic_authoritarian"]
            government.civics = ["civic_police_state","civic_functional_architecture"]

        elif empire.ideology == "stalinism":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_xenophobe","ethic_authoritarian","ethic_materialist"]
            government.civics = ["civic_police_state","civic_cutthroat_politics"]

        elif empire.ideology == "anti_revisionism":
            government.authority = "auth_oligarchic"
            government.ethics = ["ethic_egalitarian", "ethic_materialist","ethic_xenophile"]
            government.civics = ["civic_efficient_bureaucracy","civic_cutthroat_politics"]

        elif empire.ideology == "anarchist_communism":
            government.authority = "auth_democratic"
            government.ethics = ["ethic_fanatic_egalitarian","ethic_materialist"]
            government.civics = ["civic_meritocracy","civic_shadow_council"]

        ###

        elif empire.ideology == "nazism":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_militarist","ethic_authoritarian"]
            government.civics = ["civic_nationalistic_zeal","civic_corvee_system"]

        elif empire.ideology == "fascism_ideology":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_authoritarian","ethic_militarist"]
            government.civics = ["civic_nationalistic_zeal","civic_police_state"]

        elif empire.ideology == "falangism":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_authoritarian","ethic_spiritualist"]
            government.civics = ["civic_nationalistic_zeal","civic_mining_guilds"]

        elif empire.ideology == "rexism":
            government.authority = "auth_imperial"
            government.ethics = ["ethic_fanatic_authoritarian","ethic_spiritualist"]
            government.civics = ["civic_nationalistic_zeal","civic_aristocratic_elite"]

        ###

        elif empire.ideology == "despotism":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_xenophobe","ethic_pacifist"]
            government.civics = ["civic_police_state", "civic_corvee_system"]

        elif empire.ideology == "oligarchism":
            government.authority = "auth_oligarchic"
            government.ethics = ["ethic_fanatic_xenophobe","ethic_pacifist"]
            government.civics = ["civic_aristocratic_elite", "civic_cutthroat_politics"]
            
        elif empire.ideology == "moderatism":
            government.authority = "auth_oligarchic"
            government.ethics = ["ethic_xenophile","ethic_pacifist","ethic_spiritualist"]
            government.civics = ["civic_aristocratic_elite", "civic_cutthroat_politics"]

        elif empire.ideology == "centrism":
            government.authority = "auth_oligarchic"
            government.ethics = ["ethic_xenophile","ethic_pacifist","ethic_materialist"]
            government.civics = ["civic_aristocratic_elite", "civic_cutthroat_politics"]

        ###

        elif empire.ideology == "absolute_monarchy":
            government.authority = "auth_imperial"
            government.ethics = ["ethic_spiritualist","ethic_militarist","ethic_authoritarian"]
            government.civics = ["civic_feudal_society", "civic_philosopher_king"]

        elif empire.ideology == "prussian_const":
            government.authority = "auth_imperial"
            government.ethics = ["ethic_xenophile","ethic_spiritualist","ethic_militarist"]
            government.civics = ["civic_philosopher_king", "civic_aristocratic_elite"]

        elif empire.ideology == "theocracy":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_spiritualist", "ethic_xenophile"]
            government.civics = ["civic_environmentalist", "civic_free_haven"]

        elif empire.ideology == "dictatorship":
            government.authority = "auth_dictatorial"
            government.ethics = ["ethic_fanatic_authoritarian","ethic_xenophobe"]
            government.civics = ["civic_police_state", "civic_functional_architecture"]

        elif empire.ideology == "minarchism":
            government.authority = "auth_democratic"
            government.ethics = ["ethic_fanatic_egalitarian","ethic_materialist"]
            government.civics = ["civic_idealistic_foundation", "civic_meritocracy"]

        else:
            government.authority = "auth_democratic"
            government.ethics = ["ethic_egalitarian","ethic_pacifist","ethic_xenophobe"]
            government.civics = ["civic_parliamentary_system", "civic_environmentalist"]

        return government


