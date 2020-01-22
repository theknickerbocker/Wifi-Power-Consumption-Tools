''' Wrapper for analysis results


'''
class Result():

    def __init__(self, cpu_cores, cpu_freq, expected_src_rate, avg_power, actual_src_rate):
        self.cpu_cores = cpu_cores
        self.cpu_freq = cpu_freq
        self.expected_src_rate = expected_src_rate
        self.avg_power = avg_power
        self.actual_src_rate = actual_src_rate

    def to_array(self):
        return (
            self.cpu_cores,
            self.cpu_freq,
            self.expected_src_rate,
            self.avg_power,
            self.actual_src_rate
        )