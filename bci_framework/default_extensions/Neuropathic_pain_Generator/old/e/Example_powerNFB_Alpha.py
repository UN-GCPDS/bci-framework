# -*- coding: utf-8 -*-
"""
Created on Mon Mar  25 09:14:51 2022

@author: 57301
"""

import os
import sys
import numpy as np
import scipy.io as sio
import NFBPainFunctions as nfbCP

# import time
# from joblib import Parallel,delayed

# Add current working directory to sys path
sys.path.append(os.getcwd())

# =============================================================================
# Load input data
# =============================================================================

print('Loading input data ...')
data_path = 'example_data_CP.mat'
EEG_data = sio.loadmat(data_path)

# Extract data variables from the EEG_data dictionary
EEG_trials = EEG_data['X']  # EEG data per trial
fsample = int(EEG_data['fs'])  # Sampling frequency
# ch_labels = EEG_data['channels']  # Channel labels
ch_labels = [
    'Fp1',
    'Fp2',
    'F3',
    'F4',
    'C3',
    'C4',
    'P3',
    'P4',
    'O1',
    'O2',
    'F7',
    'F8',
    'T7',
    'T8',
    'P7',
    'P8',
    'Fz',
    'Cz',
    'Pz',
    'Oz',
    'FC1',
    'FC2',
    'CP1',
    'CP2',
    'FC5',
    'FC6',
    'CP5',
    'CP6',
    'TP9',
    'TP10',
    'LE',
    'RE',
    'P1',
    'P2',
    'C1',
    'C2',
    'FT9',
    'FT10',
    'AF3',
    'AF4',
    'FC3',
    'FC4',
    'CP3',
    'CP4',
    'PO3',
    'PO4',
    'F5',
    'F6',
    'C5',
    'C6',
    'P5',
    'P6',
    'PO9',
    'Iz',
    'FT7',
    'FT8',
    'TP7',
    'TP8',
    'PO7',
    'PO8',
    'Fpz',
    'PO10',
    'CPz',
    'POz',
    'FCz',
]

n = 1
target_ch = ['C3']
methodPSD = 'Fourier'
# =============================================================================
#  Estimate baseline
# =============================================================================

print('Estimating baseline ...')

alpha_lst = []
beta_lst = []
theta_lst = []
for trial in range(3):  # EGG_trial.shape[0]):
    baseline_psdband = nfbCP.NFB_powerNFBAlpha(
        EEG_trials[trial], ch_labels, fsample, target_ch, methodPSD
    )
    alpha_lst.append(baseline_psdband['alpha'])
    beta_lst.append(baseline_psdband['beta'])
    theta_lst.append(baseline_psdband['theta'])

alpha = np.mean(np.array(alpha_lst), axis=0)
beta = np.mean(np.array(beta_lst), axis=0)
theta = np.mean(np.array(theta_lst), axis=0)

psd_baseline = {'alpha': alpha, 'beta': beta, 'theta': theta}

# =============================================================================
#  Estimate target power band
# =============================================================================

print('Estimating target ...')
psd_band = nfbCP.NFB_powerNFBAlpha(
    EEG_trials[n], ch_labels, fsample, target_ch, methodPSD
)

# =============================================================================
# Comparing target and baseline
# =============================================================================

val = nfbCP.compare_PSDAlpha(psd_band, psd_baseline)
print('Modulation: {}'.format(val))
