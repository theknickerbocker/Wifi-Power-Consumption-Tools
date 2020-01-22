from monsoonanalyzer import Analyzer
import sys

def main(config_filename, load_filename, output_filename):
    analysis = Analyzer(config_filename)
    analysis.load_results(load_filename)

    analysis.pwrite_results("p"+output_filename)
    analysis.write_results(output_filename)

    sigma_fit = [1., 0.5, 0.5, 1., 0.5, 0.5, 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1. ]
    sigma_a = [0.1, 1. , 0.1, 1. , 1. , 1. , 0.1, 0.1, 1. , 1. , 1. , 1. , 1. , 1. , 1. ]
    sigma_b = [1. , 0.1, 0.1, 1. , 0.1, 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. ]
    analysis.plot_results(sigma_fit=sigma_fit, sigma_a=sigma_a, sigma_b=sigma_b)
    

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Usage: Config_Filename Loading_Filename Output_Filename")
        exit()

    config_filename = sys.argv[1]
    load_filename = sys.argv[2]
    output_filename = sys.argv[3]
    main(config_filename, load_filename, output_filename)