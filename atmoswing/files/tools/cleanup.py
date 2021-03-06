# -*- coding: utf-8 -*-

import os
import glob


def log_file_is_empty(file):
    if os.stat(file).st_size == 0:
        return True
    with open(file) as f:
        if 'Optimization has already converged.' in f.read():
            return True
    return False


def cleanup_empty_log_files(base_path):
    for x in os.listdir(base_path):
        path = os.path.join(base_path, x)
        logs = glob.glob(path + '/AtmoSwingOptimizer*.log')
        for f in logs:
            if log_file_is_empty(f):
                os.remove(f)
                print('{} removed'.format(f))


def cleanup_duplicate_ini_files(base_path):
    for x in os.listdir(base_path):
        path = os.path.join(base_path, x)
        files = glob.glob(path + '/AtmoSwing-*.ini')
        for f in files:
            os.remove(f)
            print('{} removed'.format(f))


def cleanup_old_generations(base_path):
    for x in os.listdir(base_path):
        path = os.path.join(base_path, x, 'results')
        files_generations = glob.glob(path + '/*generations.txt.gz')
        files_generations.sort()
        files_operators = glob.glob(path + '/*operators.txt.gz')
        files_operators.sort()
        for f in files_generations[:-1]:
            os.remove(f)
            print('{} removed'.format(f))
        for f in files_operators[:-1]:
            os.remove(f)
            print('{} removed'.format(f))
