# -*- coding: utf-8 -*-

import os
import glob
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import pandas as pd
from atmoswing.files.parse.optimizer import params
from collections import Counter


class PlotsGAsVariables(object):
    """Plotting the results of the Monte Carlo analysis"""

    def __init__(self, base_dir, output_path=''):
        self.fig = None
        self.base_dir = base_dir
        self.output_path = output_path
        self.marker_size_max = 50
        self.marker_size_range = 0.05
        self.marker_size_on_weight = False
        self.filter_min_weight = 0.05
        self.variables_importance_nb = 30
        self.marker_alpha = 1
        self.struct = []
        self.data = []
        self.vars = []
        self.vars_default = ['Z200', 'Z500', 'Z600', 'Z700', 'Z800', 'Z850', 'Z900', 'Z950', 'Z1000', 'ZA1000', 'PV/Z',
                             'U200', 'U300', 'U400', 'U500', 'U600', 'U700', 'U800', 'U1000', 'U10m', 'PT/U285',
                             'PT/U300', 'PT/U315', 'PT/U330', 'PT/U350', 'PT/U370', 'PT/U395', 'PV/U', 'V400', 'V500',
                             'V600', 'V700', 'V800', 'V900', 'V950', 'V1000', 'V10m', 'PT/V285', 'PT/V315', 'PT/V330',
                             'PT/V350', 'PT/V370', 'PT/V395', 'PV/V', 'PT/PRES285', 'PV/PRES', 'SLP', 'W200', 'W300',
                             'W400', 'W500', 'W600', 'W700', 'W800', 'W850', 'W900', 'W950', 'W1000', 'D300', 'D400',
                             'D800', 'D850', 'D900', 'D950', 'D1000', 'D2m', 'PT/D285', 'PT/D315', 'PT/D330', 'PT/D350',
                             'PT/D370', 'VO300', 'VO500', 'VO600', 'VO700', 'VO900', 'PV300', 'PV400', 'PV600', 'PV700',
                             'PV850', 'PV900', 'PV950', 'PT/PV285', 'PT/PV330', 'PT/PV350', 'PT/PV370', 'PT/PV395',
                             'PT/MONT285', 'PT/MONT300', 'PT/MONT330', 'PT/MONT350', 'PT/MONT370', 'RH500', 'RH600',
                             'RH700', 'RH800', 'RH850', 'RH900', 'RH950', 'RH1000', 'SH500', 'SH600', 'SH700',
                             'PT/SH315', 'PT/SH330', 'PT/SH350', 'PT/SH370', 'PT/SH395', 'TCW', 'CWAT', 'IE', 'T400',
                             'T600', 'T800', 'T850', 'T900', 'T950', 'T2m', 'PV/PT', 'SSR', 'SSRD', 'STR', 'STRD',
                             'CAPE', 'SD']
        self.use_vars_default = True
        self.stations = []
        self.crit = ['RMSE', 'S0', 'S1', 'S2', 'MD', 'DSD', 'DMV']
        self.colors = plt.get_cmap('tab10').colors
        self.markers = ['o', 'v', 's', 'P', '^', '<', '>', '8', 'p', '*', 'h', 'H', 'D', 'd', 'X']
        self.files = glob.glob(base_dir + '/**/*best_individual.txt', recursive=True)

    def show_scatter(self):
        plt.ion()
        self.__set_criteria_color()
        self.__set_marker_size()
        self.__make_scatter_plot()
        plt.show()

    def print_scatter(self, filename):
        if not self.output_path:
            raise Exception('Output path not provided')
        plt.ioff()
        self.__set_criteria_color()
        self.__set_marker_size()
        self.__make_scatter_plot()
        self.__print(filename)

    def print_syntheses(self, filename):
        if not self.output_path:
            raise Exception('Output path not provided')
        plt.ioff()
        self.__set_criteria_color()
        self.__make_syntheses_plot()
        self.__print(filename)

    def load(self):
        self.__parse_results()
        self.__list_stations()
        self.__drop_bad_scores()
        self.__list_variables()
        self.__add_variable_index()

    def __parse_results(self):
        data = []
        resCheck = params.ParamsArray(self.files[0])
        resCheck.load()
        self.struct = resCheck.struct
        labels_slct = []

        # Create labels
        for step, ptors in enumerate(self.struct):
            for ptor in range(ptors):
                labels_slct.append('var_{}_{}'.format(step, ptor))
                labels_slct.append('criterion_{}_{}'.format(step, ptor))
                labels_slct.append('weight_{}_{}'.format(step, ptor))
                labels_slct.append('time_{}_{}'.format(step, ptor))
                labels_slct.append('x_min_{}_{}'.format(step, ptor))
                labels_slct.append('x_max_{}_{}'.format(step, ptor))
                labels_slct.append('y_min_{}_{}'.format(step, ptor))
                labels_slct.append('y_max_{}_{}'.format(step, ptor))

        # Extract values
        for filename in self.files:
            results = params.ParamsArray(filename)
            results.load()
            data_slct = []
            for step, ptors in enumerate(self.struct):
                for ptor in range(ptors):
                    if ptor >= results.struct[step]:
                        continue
                    data_slct.append(results.get_variable_and_level(step, ptor))
                    data_slct.append(results.get_criterion(step, ptor))
                    data_slct.append(results.get_weight(step, ptor))
                    data_slct.append(results.get_time(step, ptor))
                    data_slct.append(results.get_xmin(step, ptor))
                    data_slct.append(results.get_xmax(step, ptor))
                    data_slct.append(results.get_ymin(step, ptor))
                    data_slct.append(results.get_ymax(step, ptor))

            vals = [int(results.get_station()), results.get_valid_score(), filename] + data_slct
            data.append(vals)

        labels = ['station', 'score', 'file'] + labels_slct
        self.data = pd.DataFrame(data, columns=labels)
        self.data.sort_values(by=['station', 'file'], inplace=True)

    def __list_variables(self):
        for step, ptors in enumerate(self.struct):
            for ptor in range(ptors):
                variables = self.data['var_{}_{}'.format(step, ptor)]
                if self.filter_min_weight > 0:
                    weight = self.data['weight_{}_{}'.format(step, ptor)]
                    variables = variables[weight >= self.filter_min_weight]
                if len(self.vars) == 0:
                    self.vars = variables
                else:
                    self.vars = self.vars.append(variables)

        self.vars = self.vars.drop_duplicates()
        self.vars = self.vars.sort_values(ascending=False)
        if self.use_vars_default:
            old_vars = list(self.vars)
            new_vars = []
            for var in self.vars_default:
                if var in old_vars:
                    new_vars.append(var)
                    old_vars.remove(var)
            if len(old_vars) > 0:
                new_vars += old_vars
            new_vars.reverse()
            self.vars = pd.Series(new_vars)
        self.vars = self.vars.reset_index(drop=True)

    def __list_stations(self):
        self.stations = self.data['station']
        self.stations = self.stations.drop_duplicates()
        self.stations = self.stations.sort_values(ascending=False)
        self.stations = self.stations.reset_index(drop=True)

    def __add_variable_index(self):
        for step, ptors in enumerate(self.struct):
            for ptor in range(ptors):
                label = 'var_index_{}_{}'.format(step, ptor)
                self.data[label] = None
                for idx, var in enumerate(self.vars):
                    self.data.loc[self.data['var_{}_{}'.format(step, ptor)] == self.vars[idx], label] = idx

    def __set_criteria_color(self):
        for step, ptors in enumerate(self.struct):
            for ptor in range(ptors):
                label = 'crit_color_{}_{}'.format(step, ptor)
                self.data[label] = None
                for icrit, crit in enumerate(self.crit):
                    indexes = self.data.loc[self.data['criterion_{}_{}'.format(step, ptor)] == crit].index
                    for index in indexes:
                        self.data[label].iloc[index] = self.colors[icrit]

    def __drop_bad_scores(self):
        for station in self.stations:
            indexes = self.data.loc[self.data['station'] == station].index
            scores = self.data['score'].loc[indexes]
            min_score = min(scores)
            sizes = self.marker_size_max * ((min_score * (1 + self.marker_size_range)) - scores) / \
                    (min_score * self.marker_size_range)
            drop_rows = indexes[sizes < 1]
            self.data.drop(index=drop_rows, inplace=True)
            self.data.reset_index(drop=True, inplace=True)

    def __set_marker_size(self):
        if self.marker_size_on_weight:
            max_weight = 0.2
            min_weight = 0.02
            for step, ptors in enumerate(self.struct):
                for ptor in range(ptors):
                    label = 'marker_size_{}_{}'.format(step, ptor)
                    self.data[label] = None
                    sizes = []
                    for weight in self.data['weight_{}_{}'.format(step, ptor)]:
                        size = self.marker_size_max * (weight - min_weight) / (max_weight - min_weight)
                        if size < 1:
                            size = 1
                        if size > self.marker_size_max:
                            size = self.marker_size_max
                        sizes.append(size)
                    self.data[label] = sizes
        else:
            self.data['marker_size'] = 0
            for station in self.stations:
                indexes = self.data.loc[self.data['station'] == station].index
                scores = self.data['score'].loc[indexes]
                min_score = min(scores)
                sizes = self.marker_size_max * ((min_score * (1 + self.marker_size_range)) - scores) / \
                        (min_score * self.marker_size_range)
                sizes[sizes < 1] = 1
                self.data.loc[indexes, 'marker_size'] = sizes

    def __make_scatter_plot(self):
        fig_height = 0.66 + float(len(self.vars)) * 3.7/25.0
        self.fig = plt.figure(figsize=(10, fig_height))
        plt.grid(axis='y', alpha=0.2)
        plt.xlim(0, len(self.data) + 1)
        plt.ylim(-1, len(self.vars))

        do_paint = False
        xticks = []
        for station in self.stations:
            indexes = self.data.loc[self.data['station'] == station].index
            index_min = min(indexes) + 1
            index_max = max(indexes) + 1
            xticks.append((index_min + index_max) / 2.0)
            if do_paint:
                plt.axvspan(index_min - 0.5, index_max + 0.5, facecolor='k', alpha=0.08)
            do_paint = not do_paint

        for step, ptors in enumerate(self.struct):
            marker = self.markers[step]
            for ptor in range(ptors):
                x = np.arange(1, len(self.data) + 1)
                variables = self.data['var_index_{}_{}'.format(step, ptor)]
                facecolors = self.data['crit_color_{}_{}'.format(step, ptor)]
                edgecolors = self.data['crit_color_{}_{}'.format(step, ptor)]
                if self.marker_size_on_weight:
                    sizes = self.data['marker_size_{}_{}'.format(step, ptor)]
                    facecolors='none'
                else:
                    sizes = self.data['marker_size']

                nodata = variables.isnull()
                if nodata.any():
                    indices = variables[nodata].index.tolist()
                    variables = variables.drop(indices)
                    edgecolors = edgecolors.drop(indices)
                    sizes = sizes.drop(indices)
                    x = np.delete(x, indices)

                plt.scatter(x, variables, marker=marker, facecolors=facecolors, edgecolors=edgecolors, s=sizes,
                            alpha=self.marker_alpha, zorder=10)
        plt.xticks(xticks, self.stations)
        plt.yticks(self.vars.index.tolist(), self.vars)
        plt.tick_params(axis='both', which='both', bottom=False, top=False,
                        labelbottom=True, left=False, right=False, labelleft=True)

        patches = []
        for idx, criteria in enumerate(self.crit):
            patches.append(mpatches.Patch(color=self.colors[idx], label=criteria, alpha=self.marker_alpha))
        plt.legend(handles=patches, title="Criteria", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), frameon=False)

        self.fig.tight_layout()

    def __make_syntheses_plot(self):
        fig_height = 2 + 2 * self.variables_importance_nb * 3.7/25.0
        self.fig, axs = plt.subplots(2, 2, figsize=(10, fig_height))
        axs[0, 1].grid(axis='y', alpha=0.2)
        axs[1, 1].grid(axis='y', alpha=0.2)
        axs[0, 0].set_ylim(0, self.variables_importance_nb + 1)
        axs[0, 1].set_ylim(0, self.variables_importance_nb + 1)
        axs[1, 0].set_ylim(0, self.variables_importance_nb + 1)
        axs[1, 1].set_ylim(0, self.variables_importance_nb + 1)

        vars_weights = [[] for i in range(len(self.vars))]
        vars_colors = [[] for i in range(len(self.vars))]
        vars_times = [[] for i in range(len(self.vars))]
        vars_xmins = [[] for i in range(len(self.vars))]
        vars_xmaxs = [[] for i in range(len(self.vars))]
        vars_ymins = [[] for i in range(len(self.vars))]
        vars_ymaxs = [[] for i in range(len(self.vars))]

        for step, ptors in enumerate(self.struct):
            for ptor in range(ptors):
                variables = self.data['var_index_{}_{}'.format(step, ptor)]
                weights = self.data['weight_{}_{}'.format(step, ptor)]
                crit_color = self.data['crit_color_{}_{}'.format(step, ptor)]
                times = self.data['time_{}_{}'.format(step, ptor)]
                xmins = self.data['x_min_{}_{}'.format(step, ptor)]
                xmaxs = self.data['x_max_{}_{}'.format(step, ptor)]
                ymins = self.data['y_min_{}_{}'.format(step, ptor)]
                ymaxs = self.data['y_max_{}_{}'.format(step, ptor)]

                nodata = variables.isnull()
                if nodata.any():
                    indices = variables[nodata].index.tolist()
                    variables = variables.drop(indices)
                    weights = weights.drop(indices)
                    crit_color = crit_color.drop(indices)
                    times = times.drop(indices)
                    xmins = xmins.drop(indices)
                    xmaxs = xmaxs.drop(indices)
                    ymins = ymins.drop(indices)
                    ymaxs = ymaxs.drop(indices)

                for i in range(len(variables)):
                    vars_weights[variables.iloc[i]].append(weights.iloc[i])
                    vars_colors[variables.iloc[i]].append(crit_color.iloc[i])
                    vars_times[variables.iloc[i]].append(times.iloc[i])
                    vars_xmins[variables.iloc[i]].append(xmins.iloc[i])
                    vars_xmaxs[variables.iloc[i]].append(xmaxs.iloc[i])
                    vars_ymins[variables.iloc[i]].append(ymins.iloc[i])
                    vars_ymaxs[variables.iloc[i]].append(ymaxs.iloc[i])

        sums = []
        counts = []
        for weights in vars_weights:
            sums.append(np.sum(weights))
            counts.append(len(weights))

        counts, sums, vars_weights, vars_colors, vars_times, vars_xmins, vars_xmaxs, vars_ymins, vars_ymaxs, vars = \
            (list(t) for t in zip(*sorted(zip(counts, sums, vars_weights, vars_colors, vars_times, vars_xmins,
                                              vars_xmaxs, vars_ymins, vars_ymaxs, self.vars.tolist()),
                                          reverse=True)))

        y = range(1, self.variables_importance_nb + 1)

        # Longitude / longitude colors
        color1 = 'tab:blue'
        color2 = 'tab:brown'
        flierprops1 = dict(marker='.', markeredgecolor=color1)
        flierprops2 = dict(marker='.', markeredgecolor=color2)

        # Print variables with criteria (color)
        count_colors = [[] for i in range(self.variables_importance_nb)]
        for i in range(self.variables_importance_nb):
            colors = vars_colors[i]
            count_col = Counter(colors)
            count_col = sorted(count_col.items(), key=lambda item: item[1], reverse=True)
            count_colors[i] = count_col

        # Simple version: ax1.barh(y, counts[0:self.variables_importance_nb])
        for i in range(self.variables_importance_nb):
            x_start = 0
            for count_col in count_colors[i]:
                x_width = count_col[1]
                color = count_col[0]
                axs[0, 0].barh(i+1, x_width, left=x_start, color=color)
                x_start += x_width

        patches = []
        for idx, criteria in enumerate(self.crit):
            patches.append(mpatches.Patch(color=self.colors[idx], label=criteria))
        axs[0, 0].legend(handles=patches, title="Criteria", loc="lower right", frameon=False)

        # Print weights
        #axs[0, 1].boxplot(vars_weights[0:self.variables_importance_nb], vert=False)

        # Print longitude
        axs[0, 1].axvspan(6, 10.5, facecolor='gray', alpha=0.3)
        box1 = axs[0, 1].boxplot(vars_xmins[0:self.variables_importance_nb], vert=False, flierprops=flierprops1)
        box2 = axs[0, 1].boxplot(vars_xmaxs[0:self.variables_importance_nb], vert=False, flierprops=flierprops2)
        for element, line_list in box1.items():
            if element == 'medians':
                continue
            for line in line_list:
                line.set_color(color1)
        for element, line_list in box2.items():
            if element == 'medians':
                continue
            for line in line_list:
                line.set_color(color2)

        # Print time
        count_times = [[] for i in range(self.variables_importance_nb)]
        h_min = 99
        h_max = 0
        for i in range(self.variables_importance_nb):
            times = vars_times[i]
            count_time = Counter(times)
            count_time = sorted(count_time.items(), key=lambda item: item[0])
            count_time_sum = np.sum(count_time, axis=0)
            count_time = [(x[0], 100 * x[1] / count_time_sum[1]) for x in count_time]
            count_times[i] = count_time
            h_min = min(float(np.min(count_time, axis=0)[0]), h_min)
            h_max = max(float(np.max(count_time, axis=0)[0]), h_max)

        cmap = plt.get_cmap('viridis')
        for i in range(self.variables_importance_nb):
            x_start = 0
            for count_time in count_times[i]:
                x_width = count_time[1]
                time = count_time[0]
                color = cmap((time - h_min) / (h_max - h_min))
                axs[1, 0].barh(i+1, x_width, left=x_start, color=color)
                x_start += x_width

        patches = []
        for hr in range(int(h_min), int(h_max) + 6, 6):
            patches.append(mpatches.Patch(color=cmap((hr - h_min) / (h_max - h_min)), label='{}'.format(hr)))
        axs[1, 0].legend(handles=patches, bbox_to_anchor=(1, -0.2), #title="Time"
                         ncol=int(1 + (h_max - h_min) / 6), loc='lower right', frameon=False)

        # Print latitudes
        axs[1, 1].axvspan(45.8, 47.8, facecolor='gray', alpha=0.3)
        box1 = axs[1, 1].boxplot(vars_ymins[0:self.variables_importance_nb], vert=False, flierprops=flierprops1)
        box2 = axs[1, 1].boxplot(vars_ymaxs[0:self.variables_importance_nb], vert=False, flierprops=flierprops2)
        for element, line_list in box1.items():
            if element == 'medians':
                continue
            for line in line_list:
                line.set_color(color1)
        for element, line_list in box2.items():
            if element == 'medians':
                continue
            for line in line_list:
                line.set_color(color2)

        min_line = mlines.Line2D([], [], color=color1, label='min')
        max_line = mlines.Line2D([], [], color=color2, label='max')
        switzerland = mpatches.Patch(color='gray', alpha=0.3, label='Switzerland')
        patches.append(mpatches.Patch(color1, label='min'))
        patches.append(mpatches.Patch(color2, label='max'))
        axs[1, 1].legend(handles=[min_line, max_line, switzerland], bbox_to_anchor=(0.5, -0.2),
                         ncol=3, loc='lower center', frameon=False)

        y_ticks = vars[0:self.variables_importance_nb]
        axs[0, 0].set_yticks(y)
        axs[0, 0].set_yticklabels(y_ticks)
        axs[0, 0].invert_yaxis()
        axs[0, 1].set_yticks(y)
        axs[0, 1].set_yticklabels(y_ticks)
        axs[0, 1].invert_yaxis()
        axs[1, 0].set_yticks(y)
        axs[1, 0].set_yticklabels(y_ticks)
        axs[1, 0].invert_yaxis()
        axs[1, 1].set_yticks(y)
        axs[1, 1].set_yticklabels(y_ticks)
        axs[1, 1].invert_yaxis()

        axs[0, 0].set_xlabel('Number of selections')
        axs[0, 1].set_xlabel('Longitude min/max')
        axs[1, 0].set_xlabel('Percentage of selected hours (%)')
        axs[1, 1].set_xlabel('Latitude min/max')

        self.fig.tight_layout()

    def __print(self, filename):
        self.fig.savefig(os.path.join(self.output_path, filename + '.pdf'))
        self.fig.savefig(os.path.join(self.output_path, filename + '.png'), dpi=300)
        plt.close(self.fig)
