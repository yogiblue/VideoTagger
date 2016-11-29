import Tkinter
import os
import numpy
import datetime
import numpy as np
import cv2
import globals

from Tkinter import Tk
from tkFileDialog import askopenfilename

import ConfigParser

Config = ConfigParser.ConfigParser()

# consider using a configuration file config.py and import variables from there and use config.speed instead
# of this global variable nonsense that is a bit of a fudge
#speed = 30 # very fast
globals.speed = 50 # quite fast
#speed = 100 # medium
globals.framesPerSecond = 1
#todo: a list of switches
# a list of behaviours and keys
# probably need some objects

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def ReadIniFile():
    print "Looking for tagger_settings.ini"
    print Config
    Config.read("tagger_settings.ini")
    numSettings = len(Config.sections())

    if numSettings == 0:
        print "Oops, no settings in tagger_settings.ini. Check your path, etc."
        exit()

    print "OK, found " + str(numSettings) + " sections"

    for section in Config.sections():
        if section == "General":
            # find the variables we need
            print ConfigSectionMap("General")
            globals.framesPerSecond = Config.getint("General", "FramesPerSecond")
            print "Video Frame Rate set at  " + str(globals.framesPerSecond) + " frames/second"
            globals.speed = Config.getint("General", "Speed")
            print "Play back speed set at  " + str(globals.speed) + " (which means nothing)"

        if "Behaviour" in section:
            print "Found a behaviour section"
            # now create a behaviour objects
            # get the type, label, and key
            if Config.get(section, "Type") == "Count":
                myBehaviour = globals.Behaviour(Config.get(section, "Type"), Config.get(section, "Label"), Config.get(section, "Key").strip("'"))
                globals.behaviourList.append(myBehaviour)

            if Config.get(section, "Type") == "Switch":
                myBehaviour = globals.Switch(Config.get(section, "Type"), Config.get(section, "Label"), Config.get(section, "Key").strip("'"))
                myBehaviour.switchSettings(Config.get(section, "SwitchLabel"), Config.get(section, "SwitchSetting"))
                globals.behaviourList.append(myBehaviour)

        print section



def main():

    ReadIniFile()

    print "Found " + str(len(globals.behaviourList)) + " behaviours"

    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    print "Using OpenCV version " + cv2.__version__

    #choose which video file to analyse

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    print(filename)

    print os.path.basename(filename)
    print os.path.dirname(filename)

    os.chdir(os.path.dirname(filename))

    simpleFile = os.path.basename(filename)

    #To do : make this a bit more general

    # find the 201* part of the 2014 and then move along 2 to get to the year part (e.g. 14)
    startpos = simpleFile.find('201') + 2
    # the time part we are interested in is 17 characters long
    endpos = startpos + 17
    datetimeString = simpleFile[startpos:endpos]
    timeString = simpleFile[startpos+9:endpos]
    #just a check

    print datetimeString
    print timeString

    fmt = '%y-%m-%d_%H-%M-%S'

    date_object = datetime.datetime.strptime(datetimeString, fmt)

    start_date_object = date_object

    print date_object

    hours = int(timeString[0:2])
    minutes = int(timeString[3:5])
    seconds  = int(timeString[6:8])

    print str(hours)
    print str(minutes)
    print str(seconds)

    cap = cv2.VideoCapture(filename)

    count = 0

    print cap

    fps = 0
    if int(major_ver)  < 3 :
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        print "Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps)
    else :
        fps = cap.get(cv2.CAP_PROP_FPS)
        print "Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps)

    if globals.framesPerSecond<>fps:
        print "Warning!!!! ini file frames per second (fps) does not match fps in video"
        print "ini file fps: " + str(globals.framesPerSecond) + " Video fps: " + str(fps)
        print "Use video setting of fps"
        globals.framesPerSecond = int(fps)

    timeVideo = 0

    # to do: check whether it exists and then initialise it

    fd = open('events_care.csv','a')

    fd.write(str(date_object))
    fd.write(', START\n')

    secondCount = 0
    femaleCount = 0
    maleCount = 0
    matingCount = 0
    nipCount = 0
    femaleWanderCount = 0
    maleWanderCount = 0

    maleActive = False
    femaleActive = False
    maleWanderActive = False
    femaleWanderActive = False

    while(cap.isOpened()):

        ret, frame = cap.read()

        if ret == False:
            print "End of video"
            break;

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #break;
        except:
            print "Closing gracefully"
            break;


        cv2.imshow('frame',gray)

        k = cv2.waitKey(globals.speed)

        #timeVideo = timeVideo + 0.1

        for item in globals.behaviourList:
            if k & 0xFF == ord(item.key):
                print item.label
                if item.type == "Switch":
                    print "Activated switch "
                    print item.switchLabel
                    if item.setting == "ON":
                        print "Turning on the switch"

                    if item.setting == "OFF":
                        print "Turning off the switch"

        if k & 0xFF == ord('q'):
            break

        if k & 0xFF == ord('f'):
            print "Female on" + str(count)
            print "Female wander off" + str(count)
            fd.write(str(date_object))
            fd.write(', female on\n')
            femaleActive = True
            femaleWanderActive = False

        if k & 0xFF == ord('d'):
            print "Female off" + str(count)
            fd.write(str(date_object))
            fd.write(', female off\n')
            femaleActive = False

        if k & 0xFF == ord('r'):
            print "Female wander on" + str(count)
            print "Female off" + str(count)
            fd.write(str(date_object))
            fd.write(', female wander on\n')
            femaleWanderActive = True
            femaleActive = False

        if k & 0xFF == ord('e'):
            print "Female wander off" + str(count)
            fd.write(str(date_object))
            fd.write(', female wander off\n')
            femaleWanderActive = False


        if k & 0xFF == ord('m'):
            print "Male on" + str(count)
            print "Male wander off" + str(count)
            fd.write(str(date_object))
            fd.write(', male on\n')
            maleActive = True
            maleWanderActive = False

        if k & 0xFF == ord('n'):
            print "Male off" + str(count)
            fd.write(str(date_object))
            fd.write(', male off\n')
            maleActive = False

        if k & 0xFF == ord('k'):
            print "Male wandering" + str(count)
            print "Male off" + str(count)
            fd.write(str(date_object))
            fd.write(', male wander on\n')
            maleWanderActive = True
            maleActive = False

        if k & 0xFF == ord('j'):
            print "Male wander off" + str(count)
            fd.write(str(date_object))
            fd.write(', male wander off\n')
            maleWanderActive = False

        if k & 0xFF == ord(' '):
            print "Mating" + str(matingCount)
            fd.write(str(date_object))
            fd.write(', mating\n')
            matingCount = matingCount + 1

        if k & 0xFF == ord('p'):
            print "Aggression" + str(nipCount)
            fd.write(str(date_object))
            fd.write(', nip\n')
            nipCount = nipCount + 1

        # to do: make this reflect the frames per second stuff
        seconds = seconds + 1
        secondCount = secondCount + 1

        if femaleActive == True:
            femaleCount = femaleCount + 1

        if maleActive == True:
            maleCount = maleCount + 1

        if maleWanderActive == True:
            maleWanderCount = maleWanderCount + 1

        if femaleWanderActive == True:
            femaleWanderCount = femaleWanderCount + 1

        date_object = date_object + datetime.timedelta(0,1)
        if seconds>=60:
            seconds = 0
            timeVideo = 0
            minutes = minutes + 1
            print hours, minutes, seconds
            print date_object

        if minutes>=60:
            minutes = 0
            hours = hours + 1

        if hours>=24:
            hours = 0


    cap.release()
    cv2.destroyAllWindows()
    fd.write(str(date_object))
    fd.write(', END\n')
    fd.close()

    fd = open('time_care.csv','a')

    fd.write(str(start_date_object))
    fd.write(',')
    fd.write(str(secondCount))
    fd.write(',')
    fd.write(str(maleCount))
    fd.write(',')
    fd.write(str(100*maleCount/secondCount))
    fd.write(',')
    fd.write(str(femaleCount))
    fd.write(',')
    fd.write(str(100*femaleCount/secondCount))
    fd.write(',')
    fd.write(str(matingCount))
    fd.write(',')
    fd.write(str(nipCount))
    fd.write(',')
    fd.write(str(maleWanderCount))
    fd.write(',')
    fd.write(str(100*maleWanderCount/secondCount))
    fd.write(',')
    fd.write(str(femaleWanderCount))
    fd.write(',')
    fd.write(str(100*femaleWanderCount/secondCount))
    fd.write('\n')

    print date_object
    print "Total seconds: ", str(secondCount)
    print "Total mating count: ", str(matingCount)
    print "Total aggression count: ", str(nipCount)
    print "Total male time on carcass: ", str(maleCount), " ", str(100*maleCount/secondCount), "%"
    print "Total female time on carcass: ", str(femaleCount), " ", str(100*femaleCount/secondCount), "%"
    print "Finished"

    fd.close()

    # todo
    # record timeString as the start time
    # wait for user to start recording, press space (or other key)
    # start computer time

    # record mating (c),
    # female on carcass(f),
    # female away from carcass (d)
    # male on carcass (m)
    # male away from carcass (n)
    # pressing space means no-one on carcass
    # pressing x ends the recording

    # write out to spreadsheet

    # event - female on carcass, start, end, duration
    #         male on carcass, start, end duration
    #         mating, duration as 1

if __name__=="__main__":
    print "Tag video utility"
    print "-----------------"
    print "A simple program to tag behaviour in video footage"
    print "You'll need a settings.ini file to configure the software"
    print ""
    main()
