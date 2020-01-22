import yaml

''' Analyzer configuration wrapper

    ARGS:
        - filename      path to the yaml configuration file


    Configuration is done in yaml format and specifies

    Specifiable values:
        - power_data_dir              Dir path location of power data
        - transmissio_data_dir        Dir path location of transmission data
        - result_dir                  Dir path location of results should be written
        - result_plot_dir             Dir path location of plotted results should be written
        - cpu_core_counts             List of core counts used
        - cpu_frequencies             List of frequencies used
        - source_rates                List of source rates used
        - offset_values               Dictionary of offset start values by [frequency][core_count]
                                      Each core count should be specified inside each frequency
        - endtime_values              Dictionary of end time values by [frequency][core_count]
                                      Each core count should be specified inside each frequency

    Example:

        ---------------------------------------------------------
        |power_data_dir          : /.../power_data_csv          |
        |transmission_data_dir   : /.../phone_data              |
        |result_dir              : /.../results/                |
        |result_plot_dir         : /.../results/graphs/         |
        |cpu_core_counts         :                              |
        |  - 1                                                  |
        |  ...                                                  |
        |cpu_frequencies         :                              |
        |  - 300000                                             |
        |  ...                                                  |
        |source_rates            :                              |
        |  - 10                                                 |
        |  ...                                                  |
        |offset_values           :                              |
        |  300000 :                                             |
        |    1 : 100                                            |
        |    ...                                                |
        |...                                                    |
        |cutoff_values           :                              |
        |  300000 :                                             |
        |    4 : 3000                                           |
        |...                                                    |
        |endtime_values          :                              |
        |  300000 :                                             |
        |    1 : 363                                            |
        |    ...                                                |
        |...                                                    |
        ---------------------------------------------------------
'''
class Config():

    def __init__(self, filename):
        config = yaml.load(open(filename))
        self.power_data_dir = config['power_data_dir']
        self.transmit_data_dir = config['transmission_data_dir']
        self.result_dir = config['result_dir']
        self.result_plot_dir = config['result_plot_dir']
        self.baseline_filenames = config['baseline_data_filenames']

        self.cpu_core_counts = config['cpu_core_counts']
        self.cpu_frequencies = config['cpu_frequencies']
        self.src_rates = config['source_rates']

        self.offsets_dict = config['offset_values']
        self.cutoffs_dict = config['cutoff_values']
        self.endtimes_dict = config['endtime_values']

    def specifies_power_data_dir(self):
        return (self.power_data_dir != None)

    def specifies_transmit_data_dir(self):
        return (self.transmit_data_dir != None)

    def specifies_result_plot_dir(self):
        return (self.result_plot_dir != None)

    def specifies_offsets(self):
        return (self.offsets_dict != None)

    def specifies_cutoffs(self):
        return (self.cutoffs_dict != None)
    
    def specifies_endtimes(self):
        return (self.endtimes_dict != None)

    def specifies_baseline(self):
        return (self.baseline_filenames != None)