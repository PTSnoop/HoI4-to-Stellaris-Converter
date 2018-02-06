# HoI4 to Stellaris Converter

They said it couldn't be done.

Well, no, actually what they said was that it *shouldn't* be done. They said a Hearts Of Iron IV to Stellaris converter was unneccessary, that people could easily just create their own custom human race inside Stellaris with whatever ethos and backstory they wanted, and that a custom HoI4-to-Stellaris converter would be a lot of work for something actually quite pointless.

And, um, they were completely right. But hey, everyone needs a hobby!

---

Features:

- Picks out the top few nations after the WW2 peace conferences and gives them their own exoplanet colonies to start from. Bigger / more industrialised countries get better planets, weaker nations get extra difficulty-setting-style penalties.
- Simulates a halfway-plausible timeline between the end of WW2 and the 2200 Stellaris start date. Possible futures include Cold Wars between major powers, nuclear war making Earth uninhabitable, climate change making Earth a bit less hospitable in a few different ways, and/or bureaucratic overhead keeping Earth as an early-space-age Primitive Civilization while the other nations bestride the heavens. Or maybe Earth is perfectly fine and is happily governed by whoever most emphatically won HoI4.
- Supports Vic2-to-HoI4 converted games, including ones that were converted from EU4 and CK2. Karlings in space, anyone?

---

Known limitations:

- Really not very well tested at all.
- No, seriously. I've only tried this out on the handful of Vic2 save files I've got lying around. If something goes wrong for you, please send me a copy of your log file and save file and/or Vic2-to-HoI4 mod so I can have a go at getting it fixed.
- Name lists get generated for each of the converted empires, but all the actual humans get their names from the default human name list instead. The only way around this would be to create separate human species with different name list - but then humans don't recognise each other as the same species. To get around this, I put a few lines in the backstory about mass migrations breaking down ethno-national boundaries. This makes more sense for freedom-loving democracies than for lebensraum-dominating fascist states, I suppose - but then maybe the ideals of the Reich got a bit lost-in-translation over hundreds of years.
- Ship names and planet names are generated from the HoI4 ship name lists. But converted games don't have those yet (everyone just uses the generic ship names), so at the moment Vic2->HoI4->Stellaris games don't have any planet names. I'll probably push some changes ot the Vic2-to-HoI4 converter at some point to address this.
- 64-bit Windows only at the moment. Linux support should be trivial, but I've not tested it yet.
- No converter frontend support yet. It shouldn't be too hard to add this, though.
- I'm planning to tie this in with the HoI4 to DEFCON converter - once I finish actually writing it.
- Probably won't work with the 2.0 update for a while.

---

Mods included:
Variable Earth Climates - https://steamcommunity.com/sharedfiles/filedetails/?id=902328397

---

Screenshots:

![20180130212452_1](https://user-images.githubusercontent.com/1518001/35595026-35cfa166-060d-11e8-9c6f-cc2eb53fe532.jpg)

![20180130214943_1](https://user-images.githubusercontent.com/1518001/35595031-38f7f0fa-060d-11e8-83b3-7a82631109df.jpg)

![20180130215044_1](https://user-images.githubusercontent.com/1518001/35595036-3aed1a7a-060d-11e8-97f1-33ecfc179b50.jpg)

![20180130222529_1](https://user-images.githubusercontent.com/1518001/35595038-3cbbe6ba-060d-11e8-94b3-b33151dca15b.jpg)
