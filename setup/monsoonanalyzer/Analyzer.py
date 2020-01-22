from monsoonanalyzer import PowerData, TransmitData, Result, ResultPlotter, Config
from colorama import Fore, Style
from datetime import datetime
from pprint import pprint
import numpy as np
import pandas as pd
import itertools as itert
import csv


''' Analyzes Monsoon power consumption data and WiFi transmission data

    ARGS:
        - config_filename       specifies the filepath to the desired configuration
'''
class Analyzer():
    def __init__(self, config_filename):
        self.config = Config.Config(config_filename)

        self.transmit_data_dict = {}
        self.power_data_dict = {}
        self.result_dict = {}

    ''' Parses phone transmission data 

        Stores in transmit_data_dict
    '''
    def parse_transmission_data(self):
        print("Parsing Transmission Data...")
        if not self.config.specifies_transmit_data_dir():
            print(f"{Fore.RED}FAILED{Style.RESET_ALL}:\tData location not specified in configuration")
            return
        time_normalization_state = f"{Fore.RED}OFF{Style.RESET_ALL}"
        if self.config.specifies_endtimes():
             time_normalization_state = f"{Fore.GREEN}ON{Style.RESET_ALL}"
        print(f"TIME NORMALIZATION:\t" + time_normalization_state)

        for cpu_freq in self.config.cpu_frequencies:
            freq_dir = self.config.transmit_data_dir + "/" + str(cpu_freq) + "khz/"

            for cpu_cores in self.config.cpu_core_counts:
                filename = freq_dir + str(cpu_cores) + "core_" + str(cpu_freq) + "khz.csv"

                print("\tParsing file: \t" + filename)
                transmit_data = TransmitData(cpu_cores, cpu_freq, filename)
                if self.config.specifies_endtimes():
                    transmit_data.normalize_timing(self.config.endtimes_dict[cpu_freq][cpu_cores])

                self.transmit_data_dict[cpu_cores,cpu_freq] = transmit_data
                
        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\ttransmission data parsed\n")

    ''' Parses phone power consumption data

        Stores in power_data_dict.

        DEPENDENT:
            - transmit_data_dict
    '''
    def parse_power_data(self):
        print("Parsing Power Data...")
        if not self.config.specifies_power_data_dir():
            print(f"{Fore.RED}FAILED{Style.RESET_ALL}:\tData location not specified in configuration")
            return
        if not self.transmit_data_dict:
            print(f"{Fore.RED}FAILED{Style.RESET_ALL}:\tTransmission data must be parsed prior to parsing power data")
            return
        time_offset_state = f"{Fore.RED}OFF{Style.RESET_ALL}"
        if self.config.specifies_offsets():
            time_offset_state = f"{Fore.GREEN}ON{Style.RESET_ALL}"
        print("TIME OFFSET:\t\t" + time_offset_state)
        baseline_state = f"{Fore.RED}OFF{Style.RESET_ALL}"
        if self.config.specifies_baseline():
            baseline_state = f"{Fore.GREEN}ON{Style.RESET_ALL}"
        print("BASELINE REDUCTION:\t" + baseline_state)
        
        baseline = 0
        if self.config.specifies_baseline():
            pass
        for cpu_freq in self.config.cpu_frequencies:
            freq_dir = self.config.power_data_dir + "/" + str(cpu_freq) + "khz/"

            for cpu_cores in self.config.cpu_core_counts:
                filename = freq_dir + str(cpu_cores) + "core_" + str(cpu_freq) + "khz.csv"
                print("\tParsing file: \t" + filename)

                power_offset = 0
                if self.config.specifies_offsets():
                    power_offset = self.config.offsets_dict[cpu_freq][cpu_cores]
                power_data = PowerData(
                    cpu_cores,
                    cpu_freq,
                    filename,
                    offset=power_offset
                )
                transmit_data = self.transmit_data_dict[cpu_cores,cpu_freq]                
                power_data.segment_by_transmit_data(transmit_data, baseline)
                self.power_data_dict[cpu_cores, cpu_freq] = power_data
            
        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tpower data parsed\n")

    ''' Determines results (Avg. power vs Source rate)

        DEPENDENT:
            - transmit_data_dict
            - power_data_dict
    '''
    def calculate_results(self):
        print("Calculating results...")
        if not self.transmit_data_dict or not self.power_data_dict:
            print(f"{Fore.RED}FAILED{Style.RESET_ALL}:\tTransmission and Power data must be parsed prior to calculating results")
            return

        for cpu_freq in self.config.cpu_frequencies:
            for cpu_cores in self.config.cpu_core_counts:
                transmit_data = self.transmit_data_dict[cpu_cores,cpu_freq]
                power_data = self.power_data_dict[cpu_cores,cpu_freq]

                for src_rate in self.config.src_rates:
                    result = Result(cpu_cores,
                    cpu_freq,
                    src_rate,
                    power_data.power_segment_dict[src_rate].avg_power,
                    transmit_data.transmit_segment_dict[src_rate].actual_src_rate)
                    self.result_dict[cpu_cores, cpu_freq, src_rate] = result

        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tresults obtained\n")

    ''' Load results into memory

        ARGS:
        - input_filename       specifies the filepath where the desired results are held
    '''
    def load_results(self, input_filename):
        print("Loading results into analyzer...")
        with open(input_filename, "r", newline="") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=",")
            for entry in csvreader:
                cpu_cores = int(entry[0])
                cpu_freq = int(entry[1])
                expected_src_rate = int(entry[2])
                actual_src_rate = float(entry[4])
                avg_power = float(entry[3])
                self.result_dict[cpu_cores,cpu_freq,expected_src_rate] = Result(
                    cpu_cores,
                    cpu_freq,
                    expected_src_rate,
                    avg_power,
                    actual_src_rate
                )
        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tresults loaded")

    def write_results(self, output_filename):
        print("Saving results to CSV file...")
        output_filename = self.config.result_dir + output_filename
        with open(output_filename, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")

            for cpu_cores in self.config.cpu_core_counts:
                for cpu_freq in self.config.cpu_frequencies:
                    for src_rate in self.config.src_rates:
                        result = self.result_dict[cpu_cores,cpu_freq,src_rate]
                        csvwriter.writerow(result.to_array())

        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tresults written to: " + output_filename)


    def pwrite_results(self, output_filename):
        print("Writing human-readable results to CSV file...")
        output_filename = self.config.result_dir + output_filename
        with open(output_filename, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=",")

            row = ["CPU CORES:"]
            for cpu_cores in self.config.cpu_core_counts:
                row += [cpu_cores] + [""] * 2 * len(self.config.cpu_frequencies)
            csvwriter.writerow(row)

            row = ["CPU FREQUENCY (khz):"]
            header_row = ["SOURCE RATE (packets/sec)"]
            for cpu_cores in self.config.cpu_core_counts:
                for cpu_freq in self.config.cpu_frequencies:
                    row += [cpu_freq] + [""] * 2
                    header_row += [""] + ["AVG POWER (mw)", "ACTUAL SOURCE RATE (packets/sec)"]
            csvwriter.writerow(row)
            csvwriter.writerow(header_row)

            for src_rate in self.config.src_rates:
                row = [src_rate]
                for cpu_cores in self.config.cpu_core_counts:
                    for cpu_freq in self.config.cpu_frequencies:
                        result = self.result_dict[cpu_cores, cpu_freq, src_rate]
                        row += [""] + [round(result.avg_power,4),round(result.actual_src_rate,4)]
                csvwriter.writerow(row)

            print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tresults written to: " + output_filename)

    def plot_results(self, sigma_fit=np.zeros(26), sigma_a=np.zeros(15), sigma_b=np.zeros(15)):
        print("Plotting Results...")
        if not self.config.specifies_result_plot_dir():
            print(f"{Fore.RED}FAILED{Style.RESET_ALL}:\tOutput location not specified in configuration")
            return
        if not self.result_dict:
            print(f"{Fore.RED}FAILED{Style.RESET_ALL}:\tNo results to plot")
            return
        src_cutoff_state = f"{Fore.RED}OFF{Style.RESET_ALL}"
        if self.config.specifies_cutoffs():
            src_cutoff_state = f"{Fore.GREEN}ON{Style.RESET_ALL}"
        print("SRC CUTOFFS:\t\t" + src_cutoff_state)
        
        src_cutoffs = {}
        if self.config.specifies_cutoffs():
            src_cutoffs = self.config.cutoffs_dict
        plotter = ResultPlotter(
            self.config.cpu_core_counts,
            self.config.cpu_frequencies,
            self.config.src_rates,
            self.result_dict,
            self.config.result_plot_dir,
            src_cutoffs=src_cutoffs)

        # plotter.plot_individual_linear()
        plotter.plot_individual_log()
        plotter.plot_combined_results()
        # plotter.plot_linear_regression_w_elbow()
        log_fit_file = plotter.write_log_curves(sigma_fit)
        plotter.reg_of_log_fit(log_fit_file, sigma_a, sigma_b)
        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tresults plotted")


    def run_model_opt(self,filename):
        if self.config.specifies_cutoffs():
            src_cutoff_state = f"{Fore.GREEN}ON{Style.RESET_ALL}"
        print("SRC CUTOFFS:\t\t" + src_cutoff_state)

        src_cutoffs = {}
        if self.config.specifies_cutoffs():
            src_cutoffs = self.config.cutoffs_dict
        plotter = ResultPlotter(
            self.config.cpu_core_counts,
            self.config.cpu_frequencies,
            self.config.src_rates,
            self.result_dict,
            self.config.result_plot_dir,
            src_cutoffs=src_cutoffs)

        print("\tStart Time: " + str(datetime.now()))
        print("\tOptimizing Best Fit...")

        sigma_fit = np.ones(len(self.config.src_rates))
        sigma_a = np.ones(len(self.config.cpu_frequencies))
        sigma_b = np.ones(len(self.config.cpu_frequencies))
        
        results = []

        for i in range(1, 21):
            val = i  * .05
            perms = [i[::-1] for i in itert.product([1,val],repeat=15)]
            for perm_fit in perms:
                sigma_fit[0:15] = perm_fit
                results.append(plotter.optimize_best_fit(sigma_fit,sigma_a,sigma_b))
                sigma_fit = np.ones(len(self.config.src_rates))
            print("\t\tDone with value: " + str(round(val,2)))

        df = pd.DataFrame(results, columns=["Best Fit Sigma", "A Sigma", "B Sigma", "Average Error Value", "Max Error Value"])
        df.to_csv("best_fit_" + filename, index=False)

        stats = []
        best_avg_err = min(df["Average Error Value"])
        best_avg_err_config = results[df['Average Error Value'].idxmin()][0]
        stats.append(('Best Average Error Value', str(best_avg_err), str(best_avg_err_config)))
    
        best_max_err = min(df["Max Error Value"])
        best_max_err_config = results[df['Max Error Value'].idxmin()][0]
        stats.append(('Best Max Error Value', str(best_max_err), str(best_max_err_config)))

        df = pd.DataFrame(stats, columns=['Category', 'Value', 'Config'])
        df.to_csv("best_fit_stats_" + filename, index=False)

        results = []

        print("\tDone")
        print("\tOptimizing Function Fit...")

        results = []

        sigma_fit = best_avg_err_config

        for i in range(1, 21):
            val = i  * .05
            perms = [i[::-1] for i in itert.product([1,val],repeat=8)]
            for perm_fit_a in perms:
                sigma_a[0:8] = perm_fit_a
                for perm_fit_b in perms:
                    sigma_b[0:8] = perm_fit_b
                    results.append(plotter.optimize_func_fit(sigma_fit,sigma_a,sigma_b))
                    sigma_b = np.ones(len(self.config.cpu_frequencies))
                sigma_a = np.ones(len(self.config.cpu_frequencies))
            print("\t\tDone with value: " + str(round(val,2)))

        df = pd.DataFrame(results, columns=["Best Fit Sigma", "A Sigma", "B Sigma", "Average Error Value", "Max Error Value"])
        df.to_csv("func_fit_" + filename, index=False)

        stats = []
        best_avg_err = min(df["Average Error Value"])
        func_best_avg_err_config = (results[df['Average Error Value'].idxmin()][1], results[df['Average Error Value'].idxmin()][2])
        stats.append(('Best Average Error Value', str(best_avg_err), str(func_best_avg_err_config)))
    
        best_max_err = min(df["Max Error Value"])
        func_best_max_err_config = (results[df['Max Error Value'].idxmin()][1], results[df['Max Error Value'].idxmin()][2])
        stats.append(('Best Max Error Value', str(best_max_err), str(func_best_max_err_config)))

        df = pd.DataFrame(stats, columns=['Category', 'Value', 'Config'])
        df.to_csv("func_fit_stats_" + filename, index=False)

        print("\tDone")
        print("\tEnd Time: " + str(datetime.now()))
        print(f"{Fore.GREEN}SUCCESS{Style.RESET_ALL}:\tmodel optimized")

        return best_avg_err_config, func_best_max_err_config
