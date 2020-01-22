from monsoonanalyzer import Analyzer
import sys

def main(config_filename, output_filename):
    analysis = Analyzer(config_filename)
    analysis.parse_transmission_data()
    analysis.parse_power_data()
    analysis.calculate_results()

    analysis.pwrite_results("p"+output_filename)
    analysis.write_results(output_filename)
    analysis.plot_results()

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Usage: Config_Filename Output_Filename")
        exit()

    config_filename = sys.argv[1]
    output_filename = sys.argv[2]
    main(config_filename, output_filename)