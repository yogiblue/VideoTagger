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
                myBehaviour = globals.Behaviour(Config.get(section, "Type"), Config.get(section, "Label"), Config.get(section, "Key").strip("'"))
                myBehaviour.setSwitchSettings(Config.get(section, "SwitchLabel"), Config.get(section, "SwitchSetting"))
                globals.behaviourList.append(myBehaviour)

                mySwitch  = globals.Switch(Config.get(section, "SwitchLabel"))
                addSwitch = True
                for switchitem in globals.switchList:
                    if switchitem.switchLabel == mySwitch.switchLabel:
                        print "Already added switch " + mySwitch.switchLabel
                        addSwitch = False

                if addSwitch==True:
                    print "Creating switch " + mySwitch.switchLabel
                    globals.switchList.append(mySwitch)

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
        print "Use file setting of fps, ignoring video information"

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
                item.increaseCount()
                print item.label + ", count " + str(item.count)
                fd.write(str(date_object))
                fd.write(', ' + item.label + '\n')

                if item.type == "Switch":
                    for switchitem in globals.switchList:
                        if item.switchName == switchitem.switchLabel:
                            if item.setting == "ON":
                                print "Turning on the switch " + switchitem.switchLabel
                                switchitem.toggleSwitch("ON")
                            elif item.setting == "OFF":
                                print "Turning off the switch "  + switchitem.switchLabel
                                switchitem.toggleSwitch("OFF")
                            else:
                                print "Mystery switch setting "  + switchitem.switchLabel


        if k & 0xFF == ord('q'):
            break

        # to do: make this reflect the frames per second stuff
        seconds = seconds + 1
        secondCount = secondCount + 1

        #check the switches
        for switchitem in globals.switchList:
            if switchitem.status=="ON":
                switchitem.increaseFrameCount()

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

    if os.path.isfile('time_care.csv') == True:
        fd = open('time_care.csv','a')
    else:
        fd = open('time_care.csv','a')
        fd.write('date, seconds,')
        for item in globals.behaviourList:
            fd.write(str(item.label))
            fd.write(',')
        for switchitem in globals.switchList:
            fd.write(str(switchitem.switchLabel))
            fd.write(',')
            fd.write('% total time')
            fd.write(',')
        fd.write('\n')

    fd.write(str(start_date_object))
    fd.write(',')
    fd.write(str(secondCount))
    fd.write(',')
    for item in globals.behaviourList:
        fd.write(str(item.count))
        fd.write(',')

    for switchitem in globals.switchList:
        fd.write(str(switchitem.frameCount))
        fd.write(',')
        fd.write(str(100*switchitem.frameCount/secondCount))
        fd.write(',')

    fd.write('\n')

    print date_object
    print "Total seconds: ", str(secondCount)

    print "Buttons pressed"
    for item in globals.behaviourList:
        print item.label + " count: " + str(item.count)
    print "Switches"
    for switchitem in globals.switchList:
        print switchitem.switchLabel + ", frames activated: " + str(switchitem.frameCount) + " " + str(100*switchitem.frameCount/secondCount) + "%"

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
