# let's use this as a global variables file
framesPerSecond = 5
speed = 100

#a list of the behaviours we want to tag
behaviourList = []


# a behaviour class
class Behaviour:

    def __init__(self, type, label, key):
        self.type = type
        self.label = label
        self.key = key

# a switch subclass so we can turn it on and off
class Switch(Behaviour):

    def switchSettings(self, switchLabel, setting):
        self.switchLabel = switchLabel
        self.setting = setting
        self.status = "OFF"

    def toggleSwitch(self, status):
        self.status = status
