
"""Transmission data for a certain cpu configuration"""
class TransmitSegment():

    def __init__(
        self,
        expected_src_rate,
        start_time,
        end_time,
        total_time,
        packets_sent):

        self.expected_src_rate = expected_src_rate
        self.start_time = start_time
        self.end_time = end_time
        self.total_time = total_time
        self.packets_sent = packets_sent
        
        self.actual_src_rate = packets_sent / (total_time / 1000000)

    def __str__(self):
        out = ("start time: " + str(self.start_time) + "\n" +
        "end time: " + str(self.end_time) + "\n" +
        "expected source rate: " + str(self.expected_src_rate) + "\n" +
        "packets sent: " + str(self.packets_sent) + "\n" +
        "actual source rate:" + str(self.actual_src_rate) + "\n")
        return out

    def __repr__(self):
        out = ("<TransmitSegment | " +
        " start_time:\t" + str(self.start_time) +
        " end_time:\t" + str(self.end_time) +
        " expected_source_rate:\t" + str(self.expected_src_rate) +
        " packets_sent:\t" + str(self.packets_sent) +
        " actual_source_rate:\t" + str(self.actual_src_rate) +
        " >")
        return out
