# -*- coding: utf-8 -*-

import pandas as pd


class ParamsArray(object):
    """Parsing of the parameters resulting from the optimizer"""

    def __init__(self, path):
        self.path = path
        self.id = 0
        self.score = ''
        self.struct = []
        self.data = []

    def load(self):
        file_struct = self.__parse_headers()
        self.data = pd.read_csv(self.path, sep='\t', skiprows=1, usecols=file_struct[0], names=file_struct[1])
        self.__remove_failed()

    def __parse_headers(self):
        fid = open(self.path, "r")
        fid.readline()
        line = fid.readline().split('\t')
        self.id = line[1]

        headers = []
        cols = []
        step = 0
        ptor = 0
        for idx, chars in enumerate(line):
            append = False
            if chars[0:10] == '|||| Step(':
                step = int(chars[10:-1])
                self.struct.append(0)
            elif chars[0:8] == '|| Ptor(':
                ptor = int(chars[8:-1])
                self.struct[step] = ptor + 1
            elif chars == 'Anb':
                label = 'Anb_{}'.format(step)
                headers.append(label)
                cols.append(idx + 1)
            elif chars == 'Level':
                append = True
                label = 'Variable_{}_{}'.format(step, ptor)
                headers.append(label)
                cols.append(idx-1)
            elif chars == 'Time':
                append = True
            elif chars == 'xMin':
                append = True
            elif chars == 'xPtsNb':
                append = True
            elif chars == 'xStep':
                append = True
            elif chars == 'yMin':
                append = True
            elif chars == 'yPtsNb':
                append = True
            elif chars == 'yStep':
                append = True
            elif chars == 'Weight':
                append = True
            elif chars == 'Criteria':
                append = True
            elif chars == 'Calib':
                headers.append(chars)
                cols.append(idx + 1)
            elif chars == 'Valid':
                headers.append(chars)
                cols.append(idx + 1)
            elif "Score" in chars:
                self.score = line[idx + 1]

            if append:
                label = '{}_{}_{}'.format(chars, step, ptor)
                headers.append(label)
                cols.append(idx + 1)

        fid.close()

        return [cols, headers]

    def __remove_failed(self):
        if self.score == 'CRPS':
            # Remove 0s
            self.data.drop(self.data[self.data.Calib == 0].index, inplace=True)

    def get_station(self):
        return self.id

    def get_station_int(self):
        return int(self.id)

    def get_steps_nb(self):
        return len(self.struct)

    def get_ptors_nb(self, step):
        return self.struct[step]

    def get_anbs(self, step):
        return int(self.data['Anb_{}'.format(step)])

    def get_variables(self, step, ptor):
        return self.data['Variable_{}_{}'.format(step, ptor)]

    def get_variable(self, step, ptor, index=0):
        var = str(self.data['Variable_{}_{}'.format(step, ptor)].iloc[index])
        if 'hgt' in var:
            var = 'Z'
        elif 'pl/z' in var:
            var = 'Z'
        elif 'pl/gpa' in var:
            var = 'ZA'
        elif 'pl/w' in var:
            var = 'W'
        elif 'pl/vvel' in var:
            var = 'W'
        elif 'pl/vo' in var:  # Vorticity (relative) (ERA-int)
            var = 'VO'
        elif 'pl/vpot' in var:  # Velocity potential (JRA55)
            var = 'VPOT'
        elif 'pl/vgrd' in var:
            var = 'V'
        elif 'pl/v' in var:
            var = 'V'
        elif 'pl/u' in var:
            var = 'U'
        elif 'pl/depr' in var:  # Dew-point depression (JRA55)
            var = 'DEPR'
        elif 'sfa/depr' in var:  # Dew-point depression (JRA55)
            var = 'DEPR'
        elif 'pl/reld' in var:  # Relative divergence (JRA55)
            var = 'RD'
        elif 'pl/d' in var:
            var = 'D'
        elif 'pt/d' in var:
            var = 'PT/D'
        elif 'pl/t' in var:
            var = 'T'
        elif 'pl/pv' in var:
            var = 'PV'
        elif 'pt/pv' in var:
            var = 'PT/PV'
        elif 'pl/rh' in var:
            var = 'RH'
        elif 'pl/r' in var:
            var = 'RH'
        elif 'pv/z' in var:
            var = 'PV/Z'
        elif 'pv/v' in var:
            var = 'PV/V'
        elif 'pv/u' in var:
            var = 'PV/U'
        elif 'pt/v' in var:
            var = 'PT/V'
        elif 'pt/u' in var:
            var = 'PT/U'
        elif 'pv/pres' in var:
            var = 'PV/PRES'
        elif 'pt/pres' in var:
            var = 'PT/PRES'
        elif 'pv/pt' in var:
            var = 'PV/PT'
        elif 'pt/q' in var:
            var = 'PT/SH'
        elif 'pl/q' in var:
            var = 'SH'
        elif 'pt/mont' in var:
            var = 'PT/MONT'
        elif 'sff/strd' in var:
            var = 'STRD'
        elif 'sff/str' in var:
            var = 'STR'
        elif 'sff/ssrd' in var:
            var = 'SSRD'
        elif 'sff/ssr' in var:
            var = 'SSR'
        elif 'sff/cape' in var:
            var = 'CAPE'
        elif 'sff/ie' in var:
            var = 'IE'
        elif 'sfa/v10' in var:
            var = 'V10m'
        elif 'sfa/u10' in var:
            var = 'U10m'
        elif 'sfa/msl' in var:
            var = 'SLP'
        elif 'sfa/rh' in var:
            var = 'RH'
        elif 'press/rh' in var:
            var = 'RH'
        elif 'press/t' in var:
            var = 'T'
        elif 'sfa/t2m' in var:
            var = 'T2m'
        elif 'sfa/sst' in var:
            var = 'SST'
        elif 'sfa/d2m' in var:
            var = 'D2m'
        elif 'sfa/sd' in var:
            var = 'SD'
        elif 'sfa/prmsl' in var:
            var = 'SLP'
        elif 'msl/pres' in var:
            var = 'SLP'
        elif 'plf/cwat' in var:
            var = 'CWAT'
        elif 'ea/cwat' in var:
            var = 'CWAT'
        elif 'tcf/cw' in var:
            var = 'CWAT'
        elif 'tc/vwv' in var:
            var = 'VWV'
        elif 'tcw' in var:
            var = 'TCW'
        elif 'omega' in var:
            var = 'W'
        return var

    def get_variable_and_level(self, step, ptor, index=0):
        var = self.get_variable(step, ptor, index)
        level = self.get_level(step, ptor, index)
        if level != 0:
            var += str(level)
        return var

    def get_levels(self, step, ptor):
        return self.data['Level_{}_{}'.format(step, ptor)]

    def get_level(self, step, ptor, index=0):
        return self.data['Level_{}_{}'.format(step, ptor)].iloc[index]

    def get_times(self, step, ptor):
        return self.data['Time_{}_{}'.format(step, ptor)]

    def get_time(self, step, ptor, index=0):
        return self.data['Time_{}_{}'.format(step, ptor)].iloc[index]

    def get_xmins(self, step, ptor):
        return self.data['xMin_{}_{}'.format(step, ptor)]

    def get_xmin(self, step, ptor, index=0):
        return self.data['xMin_{}_{}'.format(step, ptor)].iloc[index]

    def get_xmaxs(self, step, ptor):
        return self.data['xMin_{}_{}'.format(step, ptor)] + \
               (self.data['xPtsNb_{}_{}'.format(step, ptor)] - 1) * self.data['xStep_{}_{}'.format(step, ptor)]

    def get_xmax(self, step, ptor, index=0):
        return self.data['xMin_{}_{}'.format(step, ptor)].iloc[index] + \
               (self.data['xPtsNb_{}_{}'.format(step, ptor)].iloc[index] - 1) * \
               self.data['xStep_{}_{}'.format(step, ptor)].iloc[index]

    def get_xptsnbs(self, step, ptor):
        return self.data['xPtsNb_{}_{}'.format(step, ptor)]

    def get_ymins(self, step, ptor):
        return self.data['yMin_{}_{}'.format(step, ptor)]

    def get_ymin(self, step, ptor, index=0):
        return self.data['yMin_{}_{}'.format(step, ptor)].iloc[index]

    def get_ymaxs(self, step, ptor):
        return self.data['yMin_{}_{}'.format(step, ptor)] + \
               (self.data['yPtsNb_{}_{}'.format(step, ptor)] - 1) * self.data['yStep_{}_{}'.format(step, ptor)]

    def get_ymax(self, step, ptor, index=0):
        return self.data['yMin_{}_{}'.format(step, ptor)].iloc[index] + \
               (self.data['yPtsNb_{}_{}'.format(step, ptor)].iloc[index] - 1) * \
               self.data['yStep_{}_{}'.format(step, ptor)].iloc[index]

    def get_yptsnbs(self, step, ptor):
        return self.data['yPtsNb_{}_{}'.format(step, ptor)]

    def get_weight(self, step, ptor, index=0):
        return self.data['Weight_{}_{}'.format(step, ptor)].iloc[index]

    def get_weights(self, step, ptor):
        return self.data['Weight_{}_{}'.format(step, ptor)]

    def get_criterion(self, step, ptor, index=0):
        criterion = self.data['Criteria_{}_{}'.format(step, ptor)].iloc[index]
        if 'grads' in criterion:
            criterion = criterion[0:-5]
        return criterion

    def get_criteria(self, step, ptor):
        return self.data['Criteria_{}_{}'.format(step, ptor)]

    def get_calib_scores(self):
        return self.data['Calib']

    def get_calib_score(self, index=0):
        return self.data['Calib'].iloc[index]

    def get_valid_scores(self):
        return self.data['Valid']

    def get_valid_score(self, index=0):
        return self.data['Valid'].iloc[index]
