#!/usr/bin/python

import os, sys
import math, numpy
import PythonMagick

MaxRGB = 256

def ColourToRGBArray(colour):
    return [int(colour.redQuantum()/MaxRGB),int(colour.greenQuantum()/MaxRGB),int(colour.blueQuantum()/MaxRGB)]

def ColourSet(image):
    colourset = {}
    for x in range(image.size().width()):
        for y in range(image.size().height()):
            colour = str(ColourToRGBArray(image.pixelColor(x,y)))
            if not colour in colourset:
                colourset[colour] = 1
            else:
                colourset[colour] += 1
    return colourset

def CompileFlag(sourcepath, destFolder):

    if not destFolder: destFolder = "output/"
    filename = os.path.splitext(os.path.basename(sourcepath))[0]

    if os.path.exists(sourcepath) == False:
        sourceSplit = sourcepath.split("/")
        sourceSplit[-1] = sourceSplit[-1][:3]+".tga"
        basesourcepath = "/".join(sourceSplit)
        print("WARNING: Could not find \""+sourcepath+"\". Falling back to \""+basesourcepath+"\".")
        sourcepath = basesourcepath

    image = PythonMagick.Image(sourcepath)
    imagetype = image.type

    nonecolor = PythonMagick.Color(1*MaxRGB,0,0,255*MaxRGB)
    canvas = PythonMagick.Image( PythonMagick.Geometry(128,128), nonecolor )
    canvas.type = imagetype

    dropshadow = PythonMagick.Image( PythonMagick.Geometry(128,128), nonecolor )
    dropshadow.type = imagetype

    image = PythonMagick.Image(sourcepath)
    image2 = PythonMagick.Image(sourcepath)
    #image2 = PythonMagick.Image(image2)
    #image2 = PythonMagick.Image( PythonMagick.Geometry( image.size().width(), image.size().height()), nonecolor )
    #image2.composite(image, PythonMagick.Geometry(0,0,0,0), op)

    #image.sample("115x73")
    image.transform("115x73")
    image.enhance()

    dropshadow.fillColor( PythonMagick.Color(0,0,0,25*MaxRGB) )
    dropshadow.draw( PythonMagick.DrawableRectangle((128/2) - (115/2) - 1, (128/2) - (73/2) - 1, (128/2) + (115/2) + 1, (128/2) + (73/2) + 1))
    dropshadow.blur(5,5)

    x = int(128/2)
    y = int(128/2)
    #geom = PythonMagick.Geometry(int(128/2) - int(115/2), int(128/2) - int(73/2) , int(128/2) + int(115/2), int(128/2) + int(73/2))
    geom = PythonMagick.Geometry(0,0,int(128/2) - int(115/2), int(128/2) - int(73/2))
    op = PythonMagick.CompositeOperator.OverCompositeOp
    dropshadow.composite(image, geom, op)
    dropshadow.type = imagetype

    dropshadow.write(destFolder+filename+".dds")

    tiny = PythonMagick.Image(dropshadow)
    tiny.type = imagetype
    tiny.transform("24x24")
    #tiny.sample("!24x24")
    tiny.write(destFolder+"small/"+filename+".dds")

    mapflag = PythonMagick.Image( PythonMagick.Geometry(256,256), nonecolor )

    colourFrequencies = ColourSet(image2)
    sortedColours = [(k, colourFrequencies[k]) for k in sorted(colourFrequencies, key=colourFrequencies.get, reverse=True)]

    maxIntensity = 0
    minIntensity = 255
    for i in range(10):
        if i >= len(sortedColours): break
        sortedColour = sortedColours[i][0][1:-1].split(',')
        intensity = int(sortedColour[0]) + int(1.2*float(sortedColour[1])) + int(0.5*float(sortedColour[2]))
        if intensity > maxIntensity:
            maxIntensity = intensity
        if intensity < minIntensity:
            minIntensity = intensity

    for x in range(image2.size().width()):
        for y in range(image2.size().height()):
            c = ColourToRGBArray(image2.pixelColor(x,y))
            intensity = c[0] + (1.2*float(c[1])) + (0.5*float(c[2]))
            actualIntensity = (intensity - minIntensity) / (maxIntensity - minIntensity)
            if (actualIntensity < 0.0):
                actualIntensity = 0
            elif (actualIntensity > 1.0):
                actualIntensity = 255*MaxRGB
            else:
                actualIntensity = int(actualIntensity*255*MaxRGB)
            newColour = PythonMagick.Color(min(actualIntensity+MaxRGB, 255*MaxRGB),actualIntensity,actualIntensity,1*MaxRGB)
            image2.pixelColor(x,y,newColour)

    #image2.sample("!186x118")
    image2.transform("186x118")

    dropshadow2 = PythonMagick.Image( PythonMagick.Geometry(256,256), nonecolor )
    dropshadow2.type = imagetype
    dropshadow2.fillColor( PythonMagick.Color(0,0,0,25*MaxRGB) )
    dropshadow2.draw( PythonMagick.DrawableRectangle((256/2) - (186/2) - 1, (256/2) - (118/2) - 1, (256/2) + (186/2) + 1, (256/2) + (118/2) + 1))
    dropshadow2.blur(10,10)

    x = int(256/2)
    y = int(256/2)
    geom = PythonMagick.Geometry(0,0,int(256/2) - int(186/2), int(256/2) - int(118/2))
    op = PythonMagick.CompositeOperator.OverCompositeOp
    dropshadow2.composite(image2, geom, op)
    dropshadow2.type = imagetype

    dropshadow2.fillColor( PythonMagick.Color(0,0,0,255*MaxRGB) )
    dropshadow2.strokeColor( PythonMagick.Color(255*MaxRGB,255*MaxRGB,255*MaxRGB,1*MaxRGB) )
    dropshadow2.strokeWidth(2)
    dropshadow2.draw( PythonMagick.DrawableRectangle((256/2) - (186/2) - 1, (256/2) - (118/2) - 1, (256/2) + (186/2) + 1, (256/2) + (118/2) + 1))

    dropshadow2.write(destFolder+"map/"+filename+".dds")

if __name__ == "__main__":
    SetUpFolders()
    for filename in os.listdir("hoi4samples"):
        CompileFlag("hoi4samples/"+filename)
