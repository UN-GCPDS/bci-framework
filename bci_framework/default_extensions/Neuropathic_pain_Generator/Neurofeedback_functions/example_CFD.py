# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 14:13:56 2022

@author: usuario
"""

import os
import sys
import numpy as np
import scipy.io as sio
import NeuroFeedbackFunctions as nff
import time

# Add current working directory to sys path 
sys.path.append(os.getcwd())

# =============================================================================
# Load input data  
# =============================================================================

print('Loading input data ...')
data_path = 'example_data.mat'
EEG_data = sio.loadmat(data_path)

# Extract data variables from the EEG_data dictionary 
EEG_trials = EEG_data['EEG_trials'] # EEG data per trial
fsample= EEG_data['fsample'][0][0]  # Sampling frequency 
ch_labels = ['Fp1','Fp2','F7','F3','Fz','F4','F8','T7','T8','P7','P3','Pz','P4','P8','O1','02']  # Channel labels 
    
# =============================================================================
#  Estimate baseline CFD
# =============================================================================

num_trials = 50
print('Estimating baseline CFD ({} trials)...'.format(num_trials))
start_time = time.time()
CFD_lst = []
for trial in range(num_trials):
    CFD_lst.append(nff.neurofeedback_CFD(EEG_trials[:,300:1300,trial],ch_labels,fsample))
print("--- Average computation time per trial: {} seconds ---".format((time.time() - start_time)/num_trials))

baseline_CFD = np.mean(np.array(CFD_lst),axis=0)

# =============================================================================
#  Estimate target CFD
# =============================================================================

print('Estimating target CFD...')
CFD = nff.neurofeedback_CFD(EEG_trials[:,300:1300,102],ch_labels,fsample)

# =============================================================================
# Comparing target and baseline CFD
# =============================================================================

val = nff.compare_connectivity_CFD(CFD,baseline_CFD)
print('Stimulus value: {}'.format(val))



    
