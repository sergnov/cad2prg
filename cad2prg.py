#__encoding=utf-8
#d:\python32\python.exe
#Автор: Новиков Сергей, 2012
#Специально для автоматов серии L

import string
import getopt
import datetime
from datetime import date
import time
import sys
import collections
import math
import csv

class PRGCommands:
    PanelRef = "0\t"
    PanelCheck = "103\t"
    LoadTool = "105\t"
    Unload = "106\t"
    GoHome = "100\t"
    PickAndPlace = "25\t"

class Point:
    x = 0.00
    y = 0.00

    def __init__(self, x = 0.00, y = 0.00):
        self.x = x
        self.y = y

class ReadSettings:
        Delimeter = " "
        MinCountColumns = 5
        FirstIgnoreLines = 9
        BoardSide = "Top"
        GlobalReper = "GR"
        RotationReper = "RR"
        SplitEmptyDelimeters = True
        CommentChar = ";"
        Reader = {}
        BaseCommand = PRGCommands.PickAndPlace
        
class Path:
    NameCADFile = "Input\\default.pnp"
    NamePRGFile = "Output\\default.prg"
    PathToProject = sys.path[0]
    
class MathTransform:
    dx = 0.00
    dy = 0.00
    Mx = 0.0394 #1/25.4 из мм в дюймы
    My = 0.0394
    A = 0.00
    sinA = 0.00
    cosA = 1.00
    signX = 1
    signY = -1
    rotX = 0.00
    rotY = 0.00

class Columns:
    Desc1 = 0
    Desc2 = 1
    Desc3 = 6
    Side = 2
    Rotation = 5
    X = 3
    Y = 4

def OpenCADFile(value, trans):
    try:
        return csv.reader(open(trans.PathToProject+"\\"+trans.NameCADFile, 'r'), delimiter=value.Delimeter, skipinitialspace=value.SplitEmptyDelimeters)
    except IOError:
        print("Reader not work")

def InitMathTransform(value):
    value.sinA = math.sin(math.radians(value.A))
    value.cosA = math.cos(math.radians(value.A))
    value.Mx = 0.001
    value.My = 0.001
    return value

def TimeStamp():
    return date.today().strftime("%m/%d/%Y %H:%M:%S")

def PrintHeader():
    print (";L Series Pick and Place Program\r")
    print (";SAVE_DATE="+TimeStamp()+"\r")
    print (";FILE_FORMAT=2\r")
    print (";FILE_TYPE=SINGLE_HEAD\r")
    print (";\r")
    print (";Cmd    Designator A    Fdr A    Rot A    X Data A    Y Data A\r")
    print (PRGCommands.PanelRef+"Panel Ref    0    0    00.000    00.000\r")
    PanelCheckX = "{0:0>6.3f}\t".format(MathTransform.rotX)
    PanelCheckY = "{0:0>6.3f}".format(MathTransform.rotY)
    print (PRGCommands.PanelCheck+"PanelCheck    0    0\t"+PanelCheckX+PanelCheckY+"\r")
    print (PRGCommands.LoadTool+"LoadTool    1    0    00.000     00.000\r")

def PrintFooter():
    print (PRGCommands.Unload+"UnloadTool    1    0    00.000    00.000\r")
    print (PRGCommands.GoHome+"GoHome    0    0    00.000    00.000\r")
    
def NewX(X, Y, MathTransform):
    tr = MathTransform
    return tr.signX*((X+tr.dx)*tr.Mx*tr.cosA-(Y+tr.dy)*tr.My*tr.sinA)
    
def NewY(X, Y, MathTransform):
    tr = MathTransform
    return tr.signY*((X+tr.dx)*tr.Mx*tr.sinA-(Y+tr.dy)*tr.My*tr.cosA)        

def FindGlobalReper (reader, mt):
    mt = InitMathTransform(mt)
    ni = 0
    for importLine in ReadSettings.Reader:
        if ni>=ReadSettings.FirstIgnoreLines:
            if (ReadSettings.BoardSide in importLine):
                if (ReadSettings.GlobalReper in importLine):
                    x = float(importLine[Columns.X])
                    y = float(importLine[Columns.Y])
                    nX = NewX(x, y, MathTransform)
                    nY = NewY(x, y, MathTransform)
                    mt.dx = nX
                    mt.dy = nY
                    print("+++"+"{0:0>6.3f}".format(nX))
                    print("+++"+"{0:0>6.3f}".format(nY))
        ni+=1 

def FindRotationReper (reader, mt):
    mt = InitMathTransform(mt)
    ni = 0
    for importLine in ReadSettings.Reader:
        if ni>=ReadSettings.FirstIgnoreLines:
            if (ReadSettings.BoardSide in importLine):
                if (ReadSettings.RotationReper in importLine):
                    x = float(importLine[Columns.X])
                    y = float(importLine[Columns.Y])
                    nX = NewX(x, y, MathTransform)
                    nY = NewY(x, y, MathTransform)
                    mt.rotX = nX
                    mt.rotY = nY
                    print("***"+"{0:0>6.3f}".format(nX))
                    print("***"+"{0:0>6.3f}".format(nY))
        ni+=1 

def WhileTransformCAD2PRG(reader, mt):
    mt = InitMathTransform(mt)
    ni = 0
    #ReadSettings.reader.reopen()
    for importLine in ReadSettings.Reader:
        if ni>=ReadSettings.FirstIgnoreLines:
            if ReadSettings.BoardSide in importLine:
                x = float(importLine[Columns.X])
                y = float(importLine[Columns.Y])
                nX = "{0:0>6.3f}".format(NewX(x, y, MathTransform))
                nY = "{0:0>6.3f}".format(NewY(x, y, MathTransform))
                print (reader.BaseCommand+importLine[Columns.Desc1]+"_"+importLine[Columns.Desc2]+"_"
                    +importLine[Columns.Desc3]+"\t"+"1999"+"\t"+importLine[Columns.Rotation]+"\t"
                    +str(nX)+"\t"+str(nY)+"\r")
        ni+=1 
    
ReadSettings.Reader = OpenCADFile(ReadSettings, Path)
FindGlobalReper(ReadSettings, MathTransform)
ReadSettings.Reader = OpenCADFile(ReadSettings, Path)
FindRotationReper(ReadSettings, MathTransform)
PrintHeader()
ReadSettings.Reader = OpenCADFile(ReadSettings, Path)
WhileTransformCAD2PRG(ReadSettings, MathTransform)
PrintFooter()