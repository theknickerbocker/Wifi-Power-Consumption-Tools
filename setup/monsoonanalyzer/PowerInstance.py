

class PowerInstance():

    def __init__(self, timestamp, current, power, voltage):
        self.timestamp = timestamp
        self.current = current
        self.power = power
        self.voltage = voltage

    def __lt__(self, a):
        if self.timestamp <= a.timestamp:
            return True
        else:
            return False

    def __str__(self):
        out = ("timestamp: " + str(self.timestamp) + "\n" +
        "current: " + str(self.power) + "\n" +
        "power: " + str(self.power) + "\n" +
        "voltage: " + str(self.voltage))
        return out