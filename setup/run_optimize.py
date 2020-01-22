from monsoonanalyzer import Analyzer
import sys

def main(config_filename, load_filename, output_filename):
    analysis = Analyzer(config_filename)
    analysis.load_results(load_filename)

    best_avg_err_config, func_best_max_err_config = analysis.run_model_opt(output_filename)
    analysis.plot_results(best_avg_err_config, func_best_max_err_config[0], func_best_max_err_config[1])
    

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Usage: Config_Filename Loading_Filename Output_Filename")
        exit()

    config_filename = sys.argv[1]
    load_filename = sys.argv[2]
    output_filename = sys.argv[3]
    main(config_filename, load_filename, output_filename)