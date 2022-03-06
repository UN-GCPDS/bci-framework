# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 19:06:13 2022

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
EEG_trial = EEG_trials[:,300:1300,10]
fsample= EEG_data['fsample'][0][0]  # Sampling frequency 
ch_labels = ['Fp1','Fp2','F7','F3','Fz','F4','F8','T7','T8','P7','P3','Pz','P4','P8','O1','02']  # Channel labels 
   
# =============================================================================
#  Estimate baseline alpha power
# =============================================================================

num_trials = 50
print('Estimating baseline alpha power (Fz) ({} trials)...'.format(num_trials))
start_time = time.time()
AlphaFz_lst = []
for trial in range(num_trials):
    AlphaFz_lst.append(nff.neurofeedback_AlphaFz(EEG_trials[:,300:1300,trial],ch_labels,fsample))
print("--- Average computation time per trial: {} seconds ---".format((time.time() - start_time)/num_trials))

baseline_AlphaFz = np.mean(np.array(AlphaFz_lst),axis=0)

# =============================================================================
#  Estimate target alpha power
# =============================================================================

print('Estimating target alpha power (Fz)...')
AlphaFz = nff.neurofeedback_AlphaFz(EEG_trials[:,300:1300,102],ch_labels,fsample)

# =============================================================================
# Comparing target and baseline CFD
# =============================================================================

val = nff.compare_AlphaFz(AlphaFz,baseline_AlphaFz)
print('Stimulus value: {}'.format(val))



    
