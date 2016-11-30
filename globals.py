# let's use this as a global variables file
framesPerSecond = 5
speed = 100

#a list of the behaviours we want to tag, plus the switches
behaviourList = []
switchList = []


# a behaviour class
class Behaviour:

    count = 0
    switchName = ""
    setting = ""

    def __init__(self, type, label, key):
        self.type = type
        self.label = label
        self.key = key

    def increaseCount(self):
        self.count = self.count + 1

    def setSwitchSettings(self, switchName, setting):
        self.switchName = switchName
        self.setting = setting


# a switch subclass so we can turn it on and off
class Switch:

    frameCount = 0
    status = "OFF"

    def __init__(self, switchLabel):
        self.switchLabel = switchLabel

    def toggleSwitch(self, status):
        self.status = status

    def increaseFrameCount(self):
        self.frameCount = self.frameCount + 1
