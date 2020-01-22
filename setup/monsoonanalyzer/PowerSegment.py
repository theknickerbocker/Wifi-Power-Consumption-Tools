

class PowerSegment():

    def __init__(self, start_time, end_time, avg_power):
        self.start_time = start_time
        self.end_time = end_time
        self.avg_power = avg_power

    def __str__(self):
        out = ("start time: " + str(self.start_time) + "\n" +
        "end time: " + str(self.end_time) + "\n" +
        "average power: " + str(self.avg_power))
        return out

    def __repr__(self):
        out = ("<PowerSegment | " + 
        " start time: " + str(self.start_time) +
        " end time: " + str(self.end_time) +
        " average power: " + str(self.avg_power) +
        " >")
        return out