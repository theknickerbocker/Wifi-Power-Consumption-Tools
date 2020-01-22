from monsoonanalyzer import Result
from scipy.optimize import curve_fit
from scipy import stats
import itertools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class ResultPlotter():

    def __init__(self, cpu_core_counts, cpu_freqs, src_rates, results_dict, output_dir="", src_cutoffs = {}):
        self.results_dict = {}
        self.output_dir = output_dir
        self.src_cutoffs = src_cutoffs
        plt.rcParams["figure.figsize"] = (8,5)

        for key in results_dict:
            cpu_count = key[0]
            cpu_freq = key[1]
            src_rate = key[2]
            if cpu_count not in self.results_dict:
                self.results_dict[cpu_count] = {}
            if cpu_freq not in self.results_dict[cpu_count]:
                self.results_dict[cpu_count][cpu_freq] = {}
            if src_cutoffs[cpu_freq][cpu_count] and src_rate <= src_cutoffs[cpu_freq][cpu_count] :
                self.results_dict[cpu_count][cpu_freq][src_rate] = results_dict[key]

    def linear_reg(self, x, y):
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        f = lambda x: slope * x + intercept

        return ((x[0], x[-1]), (f(x[0]), f(x[-1])), slope, intercept, r_value)

    def pct_error(self, x, y, f):
        total_pct_error = 0
        if(len(y) != len(f)):
            raise Exception
        for i in zip(y,f):
            total_pct_error += abs(i[0] - i[1])/i[0]

        return total_pct_error / len(y) * 100

    def plot_individual_linear(self):
        elbows = self.find_elbows()
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                elbow = elbows[cpu_cores, cpu_freq]
                actual_src_rates = [[],[]]
                avg_power_readings = [[],[]]
                expected_src_rates = [[],[]]
                i = 0
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates[i].append(result.actual_src_rate)
                    avg_power_readings[i].append(result.avg_power)
                    expected_src_rates[i].append(result.expected_src_rate)
                    if result.expected_src_rate == elbow.expected_src_rate:
                        i = 1
                        actual_src_rates[i].append(result.actual_src_rate)
                        avg_power_readings[i].append(result.avg_power)
                        expected_src_rates[i].append(result.expected_src_rate)

                slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(expected_src_rates[0], avg_power_readings[0])
                slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(expected_src_rates[1], avg_power_readings[1])

                plt.plot(expected_src_rates[0], self.lin_func(expected_src_rates[0], slope1, intercept1), linewidth = 1, label="y = " + str(round(slope1,4)) + "x + " + str(round(intercept1,4)) + "   r^2 = " + str(round(r_value1**2, 4)))
                plt.plot(expected_src_rates[1], self.lin_func(expected_src_rates[1], slope2, intercept2), linewidth = 1, label="y = " + str(round(slope2,4)) + "x + " + str(round(intercept2,4)) + "   r^2 = " + str(round(r_value2**2, 4)))
                plt.plot(self.results_dict[cpu_cores][cpu_freq].keys(), avg_power_readings[0][0:-1] + avg_power_readings[1], 'x', linewidth = 1)
                
                plotname = str(cpu_cores) + " core(s) at " + str(cpu_freq) + "khz"
                plt.title(plotname + "(Source Rate vs Power)", fontsize = 16)
                plt.xlabel("Source Rate (pkt/sec)", fontsize = 14)
                plt.ylabel("Power (mW)", fontsize = 14)
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

                filename = self.output_dir + "_".join(plotname.split(' ')) + "_lin.png"
                plt.savefig(filename, bbox_inches = 'tight')
                plt.clf()
                plt.cla()
                plt.close()
                print("\tPlot drawn to file: " + filename)

    def plot_combined_results(self):
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)
                plt.plot(self.results_dict[cpu_cores][cpu_freq].keys(), avg_power_readings, linewidth = 1, label=str(cpu_cores)+"cores_"+str(cpu_freq)+"khz")

        filename = self.output_dir + "combined_results_plot.png"
        plt.title("Power Consumption " + "(Source Rate vs Power)", fontsize = 16)
        plt.xlabel("Source Rate (pkt/sec)", fontsize = 14)
        plt.ylabel("Power (mW)", fontsize = 14)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.savefig(filename, bbox_inches = 'tight')
        plt.clf()
        plt.cla()
        plt.close()
        print("\tPlot drawn to file: " + filename)

    def plot_linear_regression_w_elbow(self):
        elbows = self.find_elbows()
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                elbow = elbows[cpu_cores, cpu_freq]
                actual_src_rates = [[],[]]
                avg_power_readings = [[],[]]
                expected_src_rates = [[],[]]
                i = 0
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates[i].append(result.actual_src_rate)
                    avg_power_readings[i].append(result.avg_power)
                    expected_src_rates[i].append(result.expected_src_rate)
                    if result.expected_src_rate == elbow.expected_src_rate:
                        i = 1
                        actual_src_rates[i].append(result.actual_src_rate)
                        avg_power_readings[i].append(result.avg_power)
                        expected_src_rates[i].append(result.expected_src_rate)

                slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(expected_src_rates[0], avg_power_readings[0])
                slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(expected_src_rates[1], avg_power_readings[1])

                avg_r_squared = (r_value1**2 + r_value2**2) / 2
                # rgb_color = 'C' + str(cpu_cores)
                # rgb_color = (0, 0, (cpu_freq * cpu_cores) / (2457600 * 4))
                rgb_color = (((cpu_freq/101) % 100) / 100, ((cpu_freq/233) % 100) / 100 , ((cpu_freq/349) % 100) / 100)
                plt.plot(expected_src_rates[0], self.lin_func(expected_src_rates[0], slope1, intercept1), linewidth = 1, color=rgb_color, label=str(cpu_cores)+"cores_"+str(cpu_freq)+"khz    avg. r^2 = " + str(round(avg_r_squared, 4)))
                plt.plot(expected_src_rates[1], self.lin_func(expected_src_rates[1], slope2, intercept2), linewidth = 1, color=rgb_color)

        filename = self.output_dir + "lin_reg_results_w_elbow_plot.png"
        plt.title("Power Consumption " + "(Source Rate vs Power)", fontsize = 16)
        plt.xlabel("Source Rate (pkt/sec)", fontsize = 14)
        plt.ylabel("Power (mW)", fontsize = 14)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.savefig(filename, bbox_inches = 'tight')
        
        plt.xscale('log')
        filename = "_log".join(filename.split('.'))
        plt.savefig(filename, bbox_inches = 'tight')
        plt.clf()
        plt.cla()
        plt.close()
        print("\tPlot drawn to file: " + filename)

    def log_func(self, x, a,b):
        return a + b*np.log(x)

    def lin_func(self, x, m, b):
        return np.multiply(m,x) + b

    def plot_individual_log(self):
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)

                sigma = np.ones(len(src_rates))
                # sigma[0] = 0.3

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings, sigma=sigma)

                a = popt[0]
                b = popt[1]
                curvex=np.linspace(1,src_rates[-1],1000)
                curvey=self.log_func(curvex,a,b)

                err = self.pct_error(src_rates, avg_power_readings, self.log_func(src_rates, a, b))

                residuals = avg_power_readings - self.log_func(src_rates, a, b)
                ss_res = np.sum(residuals**2)
                ss_tot = np.sum((avg_power_readings-np.mean(avg_power_readings))**2)
                r_squared = 1 - (ss_res / ss_tot)

                plt.plot(src_rates, avg_power_readings, 'x')

                plt.plot(curvex, curvey, linewidth = 1, label=str(cpu_freq) + ": y = " + str(round(a,4)) + " + " + str(round(b,4)) + " log(x)   r^2 = " + str(round(r_squared, 4)) + "   avg. % error = " + str(round(err,4)))
                plotname = str(cpu_cores) + " core(s) at " + str(cpu_freq) + "khz"
                plt.title(plotname + "(Source Rate vs Power)", fontsize = 16)
                plt.xlabel("Source Rate (pkt/sec)", fontsize = 14)
                plt.ylabel("Power (mW)", fontsize = 14)
                # plt.xlim(-300,16000)
                # plt.ylim(-60, 2000)
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                # plt.xscale('log')

                filename = self.output_dir + "_".join(plotname.split(' ')) + "_log.png"
                plt.savefig(filename, bbox_inches = 'tight')
                plt.clf()
                plt.cla()
                plt.close()
                print("\tPlot drawn to file: " + filename)

    def calculate_curve(self, a, b, src_rates, avg_power_readings):
        curvex=np.linspace(1,src_rates[-1],1000)
        curvey=self.log_func(curvex,a,b)

        err = self.pct_error(src_rates, avg_power_readings, self.log_func(src_rates, a, b))

        residuals = avg_power_readings - self.log_func(src_rates, a, b)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((avg_power_readings-np.mean(avg_power_readings))**2)
        r_squared = 1 - (ss_res / ss_tot)

        return curvex,curvey,err,r_squared

    def write_log_graph(self,filename):
            filename = self.output_dir + filename
            plt.title("Power Consumption " + "(Source Rate vs Power)", fontsize = 16)
            plt.xlabel("Source Rate (pkt/sec)", fontsize = 14)
            plt.ylabel("Power (mW)", fontsize = 14)

            plt.ylim(-50,2300)
            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.xscale('log')
            plt.savefig(filename, bbox_inches = 'tight')
            plt.clf()
            plt.cla()
            plt.close()

            print("\tPlot drawn to file: " + filename)

    def plot_mixed_log_curves(self, a_func, b_func):
        best_fit_list = []
        func_list = []
        # best_a_func_b_list = []
        # func_a_best_b_list = []

        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings)

                a = popt[0]
                b = popt[1]
                a_f = a_func(cpu_freq)
                b_f = b_func(cpu_freq)

                curvex,curvey,err,r_squared = self.calculate_curve(a,b,src_rates,avg_power_readings)
                best_fit_list.append({'cpu_freq':cpu_freq,'a':a,'b':b,'curvex':curvex,'curvey':curvey,'err':err,'r_squared':r_squared})
                
                curvex,curvey,err,r_squared = self.calculate_curve(a_f,b_f,src_rates,avg_power_readings)
                func_list.append({'cpu_freq':cpu_freq,'a':a_f,'b':b_f,'curvex':curvex,'curvey':curvey,'err':err,'r_squared':r_squared})

                # curvex,curvey,err,r_squared = self.calculate_curve(a,b_f,src_rates,avg_power_readings)
                # best_a_func_b_list.append({'cpu_freq':cpu_freq,'a':a,'b':b_f,'curvex':curvex,'curvey':curvey,'err':err,'r_squared':r_squared})

                # curvex,curvey,err,r_squared = self.calculate_curve(a_f,b,src_rates,avg_power_readings)
                # func_a_best_b_list.append({'cpu_freq':cpu_freq,'a':a_f,'b':b,'curvex':curvex,'curvey':curvey,'err':err,'r_squared':r_squared})


        for best_fit in best_fit_list:
            cpu_freq = best_fit['cpu_freq']
            label = str(cpu_freq) + ": y = " + str(round(best_fit['a'],4)) + " + " + str(round(best_fit['b'],4)) + " log(x)    avg. % error = " + str(round(best_fit['err'],4))
            rgb_color = (((cpu_freq/101) % 100) / 100, ((cpu_freq/233) % 100) / 100 , ((cpu_freq/349) % 100) / 100)

            plt.plot(best_fit['curvex'], best_fit['curvey'], linewidth = 1, label=label, color=rgb_color)
        self.write_log_graph("best_fit_log_plot.png")

        for func_fit in func_list:
            cpu_freq = func_fit['cpu_freq']
            label = str(cpu_freq) + ": y = " + str(round(func_fit['a'],4)) + " + " + str(round(func_fit['b'],4)) + " log(x)    avg. % error = " + str(round(func_fit['err'],4))
            rgb_color = (((cpu_freq/101) % 100) / 100, ((cpu_freq/233) % 100) / 100 , ((cpu_freq/349) % 100) / 100)

            plt.plot(func_fit['curvex'], func_fit['curvey'], linewidth = 1, label=label,color=rgb_color)
        self.write_log_graph("func_fit_log_plot.png")

        # for best_a_func_b_fit in best_a_func_b_list:
        #     cpu_freq = best_a_func_b_fit['cpu_freq']
        #     label = str(cpu_freq) + ": y = " + str(round(best_a_func_b_fit['a'],4)) + " + " + str(round(best_a_func_b_fit['b'],4)) + " log(x)    avg. % error = " + str(round(best_a_func_b_fit['err'],4))
        #     rgb_color = (((cpu_freq/101) % 100) / 100, ((cpu_freq/233) % 100) / 100 , ((cpu_freq/349) % 100) / 100)

        #     plt.plot(best_a_func_b_fit['curvex'], best_a_func_b_fit['curvey'], linewidth = 1, label=label, color=rgb_color)
        # self.write_log_graph("best_a_func_b_log_plot.png")

        # for func_a_best_b_fit in func_a_best_b_list:
        #     cpu_freq = func_a_best_b_fit['cpu_freq']
        #     label = str(cpu_freq) + ": y = " + str(round(func_a_best_b_fit['a'],4)) + " + " + str(round(func_a_best_b_fit['b'],4)) + " log(x)    avg. % error = " + str(round(func_a_best_b_fit['err'],4))
        #     rgb_color = (((cpu_freq/101) % 100) / 100, ((cpu_freq/233) % 100) / 100 , ((cpu_freq/349) % 100) / 100)

        #     plt.plot(func_a_best_b_fit['curvex'], func_a_best_b_fit['curvey'], linewidth = 1, label=label,color=rgb_color)
        # self.write_log_graph("func_a_best_b_log_plot.png")


    def write_log_curves(self, sigma):
        log_vars = []
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)               

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings, sigma=sigma[0:len(src_rates)])

                a = popt[0]
                b = popt[1]

                log_vars.append((cpu_freq, a, b))

        filename = self.output_dir +"log_fit_values.csv"
        df = pd.DataFrame(log_vars)
        df.to_csv(filename, header=False, index=False)
        print("\tLog curve values written to: " + filename)
        return filename

    def plot_log_curves(self):
        log_vars = []
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)               

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings)

                a = popt[0]
                b = popt[1]

                curvex,curvey,err,r_squared = self.calculate_curve(a,b,src_rates,avg_power_readings)
                rgb_color = (((cpu_freq*cpu_cores/101) % 100) / 100, ((cpu_freq*cpu_cores/233) % 100) / 100 , ((cpu_freq*cpu_cores/349) % 100) / 100)
                label = str(cpu_cores) + "cores_" + str(cpu_freq) + "khz: y = " + str(round(popt[0],4)) + " + " + str(round(popt[1],4)) + " log(x)    avg. % error = " + str(round(err,4))

                # plt.plot(src_rates, avg_power_readings, 'x', color=rgb_color)
                plt.plot(curvex, curvey, linewidth = 1, label=label,color=rgb_color)
        filename = "best_fit_log_plot.png"
        self.write_log_graph(filename)
        print("\tPlot drawn to file: " + filename)

    def find_elbows(self):
        elbows = {}
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                prev = None
                prev_slope = None
                cur = None
                cur_slope = None
                count = 0
                for src_rate in self.results_dict[cpu_cores][cpu_freq]:
                    cur = self.results_dict[cpu_cores][cpu_freq][src_rate]

                    if (prev == None):
                        prev = cur
                        continue
                    if (cur_slope == None):
                        cur_slope = (cur.avg_power - prev.avg_power) / (cur.expected_src_rate - prev.expected_src_rate)
                        prev = cur
                        continue
                    prev_slope = cur_slope
                    cur_slope = (cur.avg_power - prev.avg_power) / (cur.expected_src_rate - prev.expected_src_rate)
                    if cur_slope - prev_slope < 0:
                        count += 1
                        if count >= 2:
                            elbows[cpu_cores, cpu_freq] = cur
                            break
                    else:
                        prev = cur
                        count = 0
        return elbows

    def reg_of_log_fit(self,filename, sigma_a, sigma_b):
        df = pd.read_csv(filename, names=["freq", "a", "b"])
        freq = list(df["freq"])
        a = list(df["a"]) 
        b = list(df["b"])

        popt_a, pcov = curve_fit(self.lin_func, freq, a, sigma=sigma_a)

        residuals = a - self.lin_func(freq, popt_a[0], popt_a[1])
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((a-np.mean(a))**2)
        r_squared = 1 - (ss_res / ss_tot)
        a_label = "y = " + str(round(popt_a[0],4)) + "x + " + str(round(popt_a[1],4)) + "    r^2 = " + str(round(r_squared,4))


        popt_b, pcov = curve_fit(self.lin_func, freq, b, sigma=sigma_b)
        residuals = b - self.lin_func(freq, popt_b[0], popt_b[1])
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((b-np.mean(b))**2)
        r_squared = 1 - (ss_res / ss_tot)
        b_label = "y = " + str(round(popt_b[0],4)) + "x + " + str(round(popt_b[1],4)) + "    r^2 = " + str(round(r_squared,4))

        plt.plot(freq, a, 'x', label = "A vs. CPU Frequency", color="C1")
        plt.plot(freq, self.lin_func(freq,popt_a[0],popt_a[1]), label=a_label, color="C1")
        plt.plot(freq, b, 'x', label="B vs. CPU Frequency", color="C2")
        plt.plot(freq, self.lin_func(freq,popt_b[0],popt_b[1]), label=b_label, color="C2")
        
        plt.title("y = A + B log(x)", fontsize = 16)
        plt.xlabel("CPU Frequency", fontsize = 14)
        plt.ylabel("A/B parameter", fontsize = 14)
        plt.legend(loc='lower right')

        filename = self.output_dir+"log_fit_plots.png"
        plt.savefig(filename, bbox_inches = 'tight')
        plt.clf()
        plt.cla()
        plt.close()

        print("\tPlot drawn to file: " + filename)
        self.plot_mixed_log_curves((lambda x : np.multiply(popt_a[0],x)+popt_a[1]),(lambda x : np.multiply(popt_b[0],x) + popt_b[1]))

    def optimize_best_fit(self, sigma_fit, sigma_a, sigma_b):
        best_r_squared = []
        best_err = []
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in src_rates:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)               

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings, sigma=sigma_fit[0:len(src_rates)])

                a = popt[0]
                b = popt[1]
                curvex,curvey,err,r_squared = self.calculate_curve(a,b,src_rates,avg_power_readings)
                best_r_squared.append(r_squared)
                best_err.append(err)

        return (sigma_fit, sigma_a, sigma_b, np.mean(best_err), np.amax(best_err))

    def optimize_func_fit(self, sigma_fit, sigma_a, sigma_b):
        log_vars = []
        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in src_rates:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)               

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings, sigma=sigma_fit[0:len(src_rates)])

                a = popt[0]
                b = popt[1]

                log_vars.append((cpu_freq, a, b))

        df = pd.DataFrame(log_vars,columns=["freq", "a", "b"])

        freq = list(df["freq"])
        a = list(df["a"]) 
        b = list(df["b"])

        popt_a, pcov = curve_fit(self.lin_func, freq, a, sigma=sigma_a)
        popt_b, pcov = curve_fit(self.lin_func, freq, b, sigma=sigma_b)

        a_func = (lambda x : np.multiply(popt_a[0],x)+popt_a[1])
        b_func = (lambda x : np.multiply(popt_b[0],x) + popt_b[1])

        func_r_squared = []
        func_err = []

        for cpu_cores in self.results_dict:
            for cpu_freq in self.results_dict[cpu_cores]:
                actual_src_rates = []
                avg_power_readings = []
                src_rates = [int(x) for x in self.results_dict[cpu_cores][cpu_freq].keys()]
                for src_rate in src_rates:
                    result = self.results_dict[cpu_cores][cpu_freq][src_rate]
                    actual_src_rates.append(result.actual_src_rate)
                    avg_power_readings.append(result.avg_power)               

                popt, pcov = curve_fit(self.log_func, src_rates, avg_power_readings)

                a = popt[0]
                b = popt[1]
                a_f = a_func(cpu_freq)
                b_f = b_func(cpu_freq)

                curvex,curvey,err,r_squared = self.calculate_curve(a_f,b_f,src_rates,avg_power_readings)
                func_r_squared.append(r_squared)
                func_err.append(err)
        return (sigma_fit, sigma_a, sigma_b, np.mean(func_err), np.amax(func_err))
