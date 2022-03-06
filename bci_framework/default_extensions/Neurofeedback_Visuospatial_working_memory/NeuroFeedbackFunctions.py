# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 21:06:13 2020

@author: ide2704

Effective brain connectivity functions 

Ivan De La Pava Panche, Automatics Research Group
Universidad Tecnologica de Pereira, Pereira - Colombia
email: ide@utp.edu.co

"""
# Import the necessary libraries 
import numpy as np
import scipy.spatial as sp_spatial
from scipy.linalg import fractional_matrix_power
from scipy import signal
from scipy import interpolate
from joblib import Parallel,delayed

# =============================================================================
# Kernel-based Renyi transfer entropy 
# =============================================================================

def embeddingX(x,tau,dim,u):
    """
    Time-delay embbeding of the source time series x
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Source time series 
    dim: int
        Embedding dimension 
    tau: int
        Embedding delay 
    u: int
        Interaction time

    Returns
    -------
    X_emb: ndarray of shape (samples-(tau*(dim-1))-u,dim)
        Time embedded source time series 
    """
    T = np.size(x)
    L = T -(dim-1)*tau
    firstP = T - L
    X_emb = np.zeros((L,dim))
    for i in range(L):
      for j in range(dim):
        X_emb[i,j] = x[i+firstP-(j*tau)]
    
    X_emb = X_emb[0:-u,:]
    return X_emb

def embeddingY(y,tau,dim,u):
    """
    Time-delay embbeding of the target time series y 
    
    Parameters
    ----------
    y: ndarray of shape (samples,)
        Target time series 
    dim: int
        Embedding dimension 
    tau: int
        Embedding delay 
    u: int
        Interaction time

    Returns
    -------
    Y_emb: ndarray of shape (samples-(tau*(dim-1))-u,dim)
        Time embedded target time series 
    y_t: ndarray of shape (samples-(tau*(dim-1))-u,1)
        Time shifted target time series 
    """
    T = np.size(y)
    L = T -(dim-1)*tau
    firstP = T - L
    Y_emb = np.zeros((L,dim))
    
    for i in range(L):
      for j in range(dim):
        Y_emb[i,j] = y[i+firstP-(j*tau)]
    
    y_t = y[firstP+u::] 
    y_t = y_t.reshape(y_t.shape[0],1)
    Y_emb = Y_emb[u-1:-1,:]
    return Y_emb,y_t

def GaussianKernel(X,sig_scale=1.0):
    """
    Compute Gaussian Kernel matrix    
   
    Parameters
    ----------
    X: ndarray of shape (samples,features)
        Input data 
    sig_scale: float
        Parameter to scale the kernel's bandwidth  
        
    Returns
    -------
    K: ndarray of shape (samples,samples)
        Gaussian kernel matrix
    """
    utri_ind =  np.triu_indices(X.shape[0], 1)
    dist = sp_spatial.distance.cdist(X,X,'euclidean')
    sigma = sig_scale*np.median(dist[utri_ind])
    K = np.exp(-1*(dist**2)/(2*sigma**2))
    return K

def kernelRenyiEntropy(K_lst,alpha):
    """
    Compute Renyi's entropy from kernel matrices 
    
    Parameters
    ----------
    K_lst: list
        List holding kernel matrices [ndarrays of shape (channels,channels)]
    alpha: int or float
        Order of Renyi's entropy
        
    Returns
    -------
    h: float
        Kernel-based Renyi's transfer entropy, TE(x->y)
    """
    if len(K_lst) == 1:
      K = K_lst[0]
    elif len(K_lst) == 2:
      K = K_lst[0]*K_lst[1]
    else:
      K = K_lst[0]*K_lst[1]*K_lst[2]     
    K = K/np.trace(K) 
    if alpha%1==0:
        h = np.real((1/(1-alpha))*np.log2(np.trace(np.linalg.matrix_power(K,alpha))))
    else:
        h = np.real((1/(1-alpha))*np.log2(np.trace(fractional_matrix_power(K,alpha))))
    return h

def kernelTransferEntropy(x,y,dim,tau,u,alpha,sig_scale=1.0): 
    """
    Compute kernel-based Renyi's transfer entropy from channel x to channel y
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Source time series 
    y: ndarray of shape (samples,)
        Target time series 
    dim: int
        Embedding dimension 
    tau: int
        Embedding delay 
    u: int
        Interaction time
    alpha: int or float
        Order of Renyi's entropy
    sig_scale: float
        Parameter to scale the kernel's bandwidth  

    Returns
    -------
    TE: float
        Kernel-based Renyi's transfer entropy, TE(x->y)
    """
    dim = int(dim)
    tau = int(tau)
    u = int(u)
    
    X_emb = embeddingX(x,tau,dim,u)
    Y_emb, y_t = embeddingY(y,tau,dim,u)
    
    K_X_emb = GaussianKernel(X_emb,sig_scale)
    K_Y_emb = GaussianKernel(Y_emb,sig_scale)
    K_y_t = GaussianKernel(y_t,sig_scale)    
    
    h1 = kernelRenyiEntropy([K_X_emb,K_Y_emb],alpha)
    h2 = kernelRenyiEntropy([K_X_emb,K_Y_emb,K_y_t],alpha)
    h3 = kernelRenyiEntropy([K_Y_emb,K_y_t],alpha)
    h4 = kernelRenyiEntropy([K_Y_emb],alpha)
    
    TE = h1 - h2 + h3 - h4
    return TE

def kernelTransferEntropy_PAC_Ch(X,ch_pair,Dim,Tau,U,alpha,freq_ph,freq_amp,time,sig_scale=1.0):
    """
    Compute directed phase-amplitude interactions through kernel-based Renyi's phase transfer
    entropy between a pair channels 
    
    Parameters
    ----------
    X: ndarray of shape (channels,samples)
        Input time series (number of channels x number of samples)
    Dim: ndarray of shape (channels,)
        Embedding dimension for each channel
    Tau: ndarray of shape (channels,)
        Embedding delay for each channel
    U: ndarray of shape (channels,)
        Interaction times for each channel pair and direction of interaction
    alpha: int or float
        Order of Renyi's entropy
    freq_ph: ndarray of shape (frequencies_ph,)
        Frequencies of interest for phase extraction, in Hz
    freq_amp: ndarray of shape (frequencies_amp,)
        Frequencies of interest for amplitude extraction, in Hz
    time: ndarray of shape (samples,)
        Time vector (must be sampled at the sampling frequency of X)
    sig_scale: float
        Parameter to scale the kernel's bandwidth  

    Returns
    -------
    TE_pac: ndarray of shape (frequencies_ph,frequencies_amp) 
        Directed PAC estimated through kernel-based Renyi's phase transfer
        entropy
    """
    
    X = X[[ch_pair[0],ch_pair[1]],:]
    tau = Tau[ch_pair[1]]
    dim = Dim[ch_pair[1]]
    u = U[ch_pair[1]]
    
    num_freq_ph = np.size(freq_ph)
    num_freq_amp = np.size(freq_amp)
    TE_pac = np.zeros((num_freq_ph,num_freq_amp))
    
    src = X[0,:]
    src = src.reshape((1,len(src)))
    trg = X[1,:]
    trg = trg.reshape((1,len(trg)))

    # Wavelet decomposition 
    src_ph = Wavelet_Trial_Dec(src,time,freq_ph,component='phase')[0,:,:]
    src_ph = src_ph.T
    trg_amp = Wavelet_Trial_Dec(trg,time,freq_amp,component='amp')[0,:,:]
    trg_amp = trg_amp.T
    
    trg_amp_ph_lst = []
    for kk in range(num_freq_amp):
        trg_amp_aux = trg_amp[kk,:].reshape((1,len(trg_amp[kk,:])))
        if (trg.shape[1] % 2) == 0:
            time = time.flatten()
            trg_amp_ph_lst.append(np.transpose(Wavelet_Trial_Dec(trg_amp_aux,time[:-1],freq_ph,component='phase')[0,:,:]))
        else:
            trg_amp_ph_lst.append(np.transpose(Wavelet_Trial_Dec(trg_amp_aux,time,freq_ph,component='phase')[0,:,:]))
    
    for j in range(num_freq_amp):
        # Embedding parameters 
        tau = int(tau)
        dim = int(dim)  
        for i in range(num_freq_ph):
            # Delay time 
            u = int(u)
        
            # Target channel  
            y = trg_amp_ph_lst[j][i,:]
            # Source channel 
            x = src_ph[i,:]
            
            # Time embeddings for y 
            Y_emb, y_t = embeddingY(y,tau,dim,u)
            # Kernels for y's time embeddings 
            K_Y_emb = GaussianKernel(Y_emb,sig_scale)
            K_y_t = GaussianKernel(y_t,sig_scale)   
            # Entropies 
            h3 = kernelRenyiEntropy([K_Y_emb,K_y_t],alpha)
            h4 = kernelRenyiEntropy([K_Y_emb],alpha)
    
            # Time embedding for x 
            X_emb = embeddingX(x,tau,dim,u)
            # Kernels for x's time embedding
            K_X_emb = GaussianKernel(X_emb,sig_scale)
            # Entropies 
            h1 = kernelRenyiEntropy([K_X_emb,K_Y_emb],alpha)
            h2 = kernelRenyiEntropy([K_X_emb,K_Y_emb,K_y_t],alpha)
           
            # Transfer entropy
            TE_pac[i,j] =  h1 - h2 + h3 - h4
            
    return TE_pac

# =============================================================================
# Embedding functions 
# =============================================================================

def autocorrelation(x):
    """
    Autocorrelation of x
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Input time series 

    Returns
    -------
    act: ndarray of shape (samples,) 
        Autocorrelation 
    """
    xp = (x - np.mean(x))/np.std(x)
    result = np.correlate(xp, xp, mode='full')
    auto_corr = result[int(result.size/2):]/len(xp)
    return auto_corr

def autocorr_decay_time(x,maxlag):
    """ 
    Autocorrelation decay time (embedding delay)
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Input time series 
    maxlag: int
        Maximum embedding delay

    Returns
    -------
    act: int 
        Embedding delay  
    """
    autocorr = autocorrelation(x)
    thresh = np.exp(-1)
    aux = autocorr[0:maxlag];
    aux_lag = np.arange(0,maxlag)
    if len(aux_lag[aux<thresh]) == 0:
        act = maxlag
    else:
        act = np.min(aux_lag[aux<thresh])
    return act

def cao_criterion(x,d_max,tau):
    """ 
    Cao's criterion (embedding dimension)
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Input time series 
    d_max: int
        Maximum embedding dimension 
    tau: int
        Embedding delay

    Returns
    -------
    dim: int 
        Embedding dimension 
    """
    tau = int(tau)
    N = len(x)
    d_max = int(d_max)+1 
    x_emb_lst = []
    
    for d in range(d_max):
        # Time embedding 
        T = np.size(x)
        L = T-(d*tau)
        if L>0:
            FirstP = T-L
            x_emb = np.zeros((L,d+1))
            for ii in range(0,L):
                for jj in range(0,d+1): 
                    x_emb[ii,jj] = x[ii+FirstP-(jj*tau)]
            x_emb_lst.append(x_emb)
    
    d_aux = len(x_emb_lst)
    E = np.zeros(d_aux-1)
    for d in range(d_aux-1):
        emb_len = N-((d+1)*tau)
        a = np.zeros(emb_len)
        for i in range(emb_len): 
            var_den = x_emb_lst[d][i,:]-x_emb_lst[d][0:emb_len,:]
            inf_norm_den = np.linalg.norm(var_den,np.inf,axis=1)
            inf_norm_den[inf_norm_den==0] = np.inf
            den = np.min(inf_norm_den)
            ind = np.argmin(inf_norm_den)
            num = np.linalg.norm(x_emb_lst[d+1][i,:]-x_emb_lst[d+1][ind,:],np.inf)
            a[i] = num/den
        E[d] = np.sum(a)/emb_len
    
    E1 = np.roll(E,-1)  # circular shift
    E1 = E1[:-1]/E[:-1]
    
    dim_aux = np.zeros([1,len(E1)-1])
    
    for j in range(1,len(E1)-1):
        dim_aux[0,j] = E1[j-1]+E1[j+1]-2*E1[j]
    dim_aux[dim_aux==0] = np.inf
    dim = np.argmin(dim_aux)+1

    return dim

# =============================================================================
# Cross-frequency directionality 
# =============================================================================

def win_segmentation(x,n_win,overlap):
    """
    Segment time series x into windows of n_win points with an overlap of overlap
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Time series 
    n_win: integer
        Number of data points per window 
    overlap: float
        Percentage of overlap among the segmentation windows
    
    Returns
    -------
    seg_signal: ndarray of shape
        Time series segmented into multiple windows   
    """
    n_signal = len(x); # Time series lenght
    n_overlap = np.round((1-overlap)*n_win) # No overlap length  
    
    n_segments = int(np.fix((n_signal-n_win+n_overlap)/n_overlap)) # Number of segments
    ind = n_overlap*(np.arange(n_segments))   # Segment indices  
    ind = ind.astype(int)
    inds = np.arange(n_win)
    
    # Time series segmentation
    inds = np.reshape(inds,(-1,len(inds)))
    ind = np.reshape(ind,(-1,len(ind))).T
    seg_signal = x[np.repeat(inds,n_segments,axis=0)+np.repeat(ind,inds.shape[1],axis=1)]
    
    return seg_signal

def PSI(x,y,freq_range,fs):
    """
    Compute the phase slope index (PSI) from channel x to channel y
    
    Parameters
    ----------
    x: ndarray of shape (samples,)
        Source time series 
    y: ndarray of shape (samples,)
        Target time series 
    freq_range: ndarray of shape (frequencies,)
        Frequencies of interest, in Hz
    fs: float
        Sampling frequency
    
    Returns
    -------
    psi: float
        PSI(x->y) at the freq_range  
    """
    
    # Spectrums 
    x = x.flatten()
    y = y.flatten()
    n_win = int(np.floor(len(x)/4.5))
    overlap = n_win//2
    nfft = int(np.max([2**np.ceil(np.log2(n_win)),256]))
    f, Sxy = signal.csd(y,x,fs,window='hamming',nperseg=n_win,noverlap=overlap,nfft=nfft,detrend=False)
    f, Sxx = signal.csd(x,x,fs,window='hamming',nperseg=n_win,noverlap=overlap,nfft=nfft,detrend=False)
    f, Syy = signal.csd(y,y,fs,window='hamming',nperseg=n_win,noverlap=overlap,nfft=nfft,detrend=False)
    
    # Imaginary coherence 
    icoh = Sxy/np.sqrt(Sxx*Syy)
    
    # Phase Slope Index 
    aux = np.conj(icoh[:-1])*icoh[1::]
    # aux_seg = win_segmentation(aux[:-1],5,0.7)
    aux_seg = win_segmentation(aux[:-1],3,0.7)
    psi_aux = np.imag(np.sum(aux_seg,axis=1))

    # Interpolating the PSI for the frequencies of interest
    # f_psi = f[2:-1:2] 
    f_psi = f[1:-1]
    interp_fun = interpolate.interp1d(f_psi[:len(psi_aux)], psi_aux)
    psi = interp_fun(freq_range)   # use interpolation function returned by `interp1d`
    
    return psi

def CFD_Ch(X,ch_pair,freq_ph,freq_amp,time,fs):
    """
    Compute the cross-frequency directionality (CFD) between a pair channels 
    
    Parameters
    ----------
    X: ndarray of shape (channels,samples)
        Input time series (number of channels x number of samples)
    ch_pair: list 
        Channel pair of interest
    freq_ph: ndarray of shape (frequencies_ph,)
        Frequencies of interest for phase extraction, in Hz
    freq_amp: ndarray of shape (frequencies_amp,)
        Frequencies of interest for amplitude extraction, in Hz
    time: ndarray of shape (samples,)
        Time vector (must be sampled at the sampling frequency of X)
    fs: float
        Sampling frequency

    Returns
    -------
    CFD_pac: ndarray of shape  
        Cross frequency directionality 
    """
    X = X[[ch_pair[0],ch_pair[1]],:]
    
    num_freq_ph = np.size(freq_ph)
    num_freq_amp = np.size(freq_amp)
    CFD_pac = np.zeros((num_freq_ph,num_freq_amp))
    
    src = X[0,:]
    src = src.reshape((1,len(src)))
    trg = X[1,:]
    trg = trg.reshape((1,len(trg)))
    
    # Wavelet decomposition 
    trg_amp = Wavelet_Trial_Dec(trg,time,freq_amp,component='amp')[0,:,:]
    trg_amp = trg_amp.T

    # CFD
    for j in range(num_freq_amp):
        CFD_pac[:,j] = PSI(src,trg_amp[j,:],freq_ph,fs)  
            
    return CFD_pac

# =============================================================================
# Wavelet transform
# =============================================================================

def Morlet_Wavelet(data,time,freq):
    """
    Morlet wavelet decomposition 
    
    Parameters
    ----------
    data: ndarray of shape (samples,)
        Input signal 
    time: ndarray of shape (samples,)
        Time vector (must be sampled at the sampling frequency of data, 
        best practice is to have time=0 at the center of the wavelet)
    freq: ndarray of shape (frequencies,)
        Frequencies to evaluate in Hz
        
    Returns
    -------
    dataW: dict of keys {'amp','filt','phase','f'}
        Dictionary containing the Morlet wavelet decomposition of data
        'amp': ndarray of shape (frequencies,num_samples) holding the amplitude envelopes at each freq
        'filt': ndarray of shape (frequencies,num_samples) holding the filtered signals at each freq
        'phase': ndarray of shape (frequencies,num_samples) holding the phase time series at each freq
        'f': ndarray of shape (frequencies,) holding the evaluated frequencies in Hz
        (If samples is odd, num_samples = samples, otherwise num_samples = samples-1)
    """
    # =============================================================================
    # Create the Morlet wavelets
    # =============================================================================
    num_freq = len(freq); 
    cmw = np.zeros([data.shape[0],num_freq],dtype = 'complex_')
    
    # Number of cycles in the wavelets 
    range_cycles = [3,10]
    max_freq = 60 
    freq_vec = np.arange(1,max_freq+1)
    nCycles_aux = np.logspace(np.log10(range_cycles[0]),np.log10(range_cycles[-1]),len(freq_vec))
    nCycles = np.array([nCycles_aux[np.argmin(np.abs(freq_vec - freq[i]))] 
                        for i in range(num_freq)])
    
    for ii in range(num_freq): 
        # create complex sine wave
        sine_wave = np.exp(1j*2*np.pi*freq[ii]*time)
        
        # create Gaussian window
        s = nCycles[ii]/(2*np.pi*freq[ii]) #this is the standard deviation of the gaussian
        gaus_win  = np.exp((-time**2)/(2*s**2))
        
        # now create Morlet wavelet
        cmw[:,ii] = sine_wave*gaus_win
        
    # =============================================================================
    # Convolution 
    # =============================================================================
    
    # Define convolution parameters 
    nData = len(data)
    nKern = cmw.shape[0]
    nConv = nData + nKern - 1
    half_wav = int(np.floor(cmw.shape[0]/2)+1)
    
    # FFTs
    
    # FFT of wavelet, and amplitude-normalize in the frequency domain
    cmwX = np.fft.fft(cmw,nConv,axis=0)
    cmwX = cmwX/np.max(cmwX,axis=0)
        
    # FFT of data
    dataX = np.fft.fft(data,nConv)
    dataX = np.repeat(dataX.reshape([-1,1]),num_freq,axis=1)
    
    # Convolution...
    data_wav = np.fft.ifft(dataX*cmwX,axis=0)
    
    # Cut 1/2 of the length of the wavelet from the beginning and from the end
    data_wav = data_wav[half_wav-2:-half_wav,:]
    
    # Extract filtered data, amplitude and phase 
    data_wav = data_wav.T
    dataW = {}
    dataW['filt'] = np.real(data_wav)
    dataW['amp'] = np.abs(data_wav)
    dataW['phase'] = np.angle(data_wav)
    dataW['f'] = freq 
    
    return dataW

def Wavelet_Trial_Dec(data,time,freq,component ='phase'):
    """
    Morlet wavelet decomposition for multiple channels 
    
    Parameters
    ----------
    data: ndarray of shape (channels,samples)
        Input signals (number of channels x number of samples)
    time: ndarray of shape (samples,)
        Time vector (must be sampled at the sampling frequency of data)
    freq: ndarray of shape (frequencies,)
        Frequencies to evaluate in Hz
    component: {'filt','amp','phase'}
       Component of interest from the wavelet decomposition at each frequency 
       in freq (filt: filtered data, amp: amplitude envelope, phase: phase)

    Returns
    -------
    wav_dec: ndarray of shape (channels,num_samples,frequencies) 
        Array containing the wavelet decomposition of data at the target
        frequencies (If samples is odd, num_samples = samples, otherwise 
        num_samples = samples-1)

    """
    if np.size(freq) == 1:
        freq = [freq]

    # Time centering 
    t = (time.flatten())/1000 # ms to s
    t = t - t[0]
    t = t-(t[-1]/2) # best practice is to have time=0 at the center of the wavelet

    if (data.shape[1] % 2) == 0:
        wav_dec = np.zeros([data.shape[0],data.shape[1]-1,len(freq)])
    else:
        wav_dec = np.zeros([data.shape[0],data.shape[1],len(freq)])

    for ch in range(data.shape[0]):
       
        # Data detrending
        ch_data = data[ch,:]
        ch_data = ch_data - np.mean(ch_data)
        
        # Data decomposition 
        dataW = Morlet_Wavelet(ch_data,t,freq)
        wav_dec[ch,:,:] = dataW[component].T
    
    return wav_dec
            
# =============================================================================
# Connectivity-based Neurofeedback Functions 
# =============================================================================

def neurofeedback_CFD(data,ch_labels,fs): 
    """
    Compute the average CFD (Frontal/pre-frontal theta to parietal/occipital alpha) 
    for a 1 second long EEG trial (epoch).   
    
    Parameters
    ----------
    data: ndarray of shape (channels,samples)
        Input time series (number of channels x number of samples)
    ch_labels: list
        EEG channel labels 
    fs: float
        Sampling frequency (Hz)
    
    Returns
    -------
    CFD_mean: ndarray of shape (channels,channels)
        Average CFD for the channels and frequency bands of interest   
    """
    
    # Frequency values to test
    freq_ph = [4,6] # frequency of wavelet (phase), in Hz 
    freq_amp = [8,10,12] # frequency of wavelet (amplitude), in Hz 
    num_freq_ph = len(freq_ph)
    num_freq_amp = len(freq_amp)
    
    # Time vector
    t_vec = 1000*np.arange(0,1,1/fs)    
    
    # Channel combination list
    num_ch = len(ch_labels)             # Number of channels 
    # source_ch_labels = ['Fp1','Fp2','F7','F3','Fz','F4','F8']
    # target_ch_labels = ['P7','P3','Pz','P4','P8','O1','02']
    source_ch_labels = ['F3','F4']
    target_ch_labels = ['P3','P4']
    try:
        source_ch = [ch_labels.index(ch) for ch in source_ch_labels]
    except ValueError:
        print("Error! Required channel not found...")
    try:
        target_ch = [ch_labels.index(ch) for ch in target_ch_labels]
    except ValueError:
        print("Error! Required channel not found...")
    xv, yv = np.meshgrid(source_ch,target_ch,indexing='ij')
    ch_lst_aux = list(np.vstack((np.reshape(xv,-1),np.reshape(yv,-1))).T)
    ch_pair_lst = [[ch[0],ch[1]] for ch in ch_lst_aux if ch[0]!=ch[1]]
    
    # Compute the CFD
    CFD_cfi_aux = Parallel(n_jobs=-1,verbose=0)(delayed(CFD_Ch) 
                                    (data,ch_pair,freq_ph,freq_amp,t_vec,fs) for ch_pair in ch_pair_lst)
    CFD_matrix = np.zeros((num_ch,num_ch,num_freq_ph*num_freq_amp))
    for ii,ch_pair in enumerate(ch_pair_lst):
        CFD_matrix[ch_pair[0],ch_pair[1],:] = CFD_cfi_aux[ii].flatten() 
    CFD_mean = np.mean(CFD_matrix,axis=2)
    
    return CFD_mean


def neurofeedback_kTE_PAC(data,ch_labels,fs): 
    """
    Compute the average PAC through kTE (Frontal/pre-frontal theta to parietal/occipital alpha) 
    for a 1 second long EEG trial (epoch).   
    
    Parameters
    ----------
    data: ndarray of shape (channels,samples)
        Input time series (number of channels x number of samples)
    ch_labels: list
        EEG channel labels 
    fs: float
        Sampling frequency (Hz)
    
    Returns
    -------
    kTE_mean: ndarray of shape (channels,channels)
        Average PAC kTE for the channels and frequency bands of interest   
    """
    # Data downsampling (fs: 1000 Hz -> 500 Hz)
    n = 2
    data = data[:,::n]
    fs = fs//n
       
    # Frequency values to test
    freq_ph = [4,6] # frequency of wavelet (phase), in Hz 
    freq_amp = [8,10,12] # frequency of wavelet (amplitude), in Hz 
    num_freq_ph = len(freq_ph)
    num_freq_amp = len(freq_amp)
    
    # Time vector
    t_vec = 1000*np.arange(0,1,1/fs)    
    
    # Channel combination list
    num_ch = len(ch_labels)             # Number of channels 
    # source_ch_labels = ['Fp1','Fp2','F7','F3','Fz','F4','F8']
    # target_ch_labels = ['P7','P3','Pz','P4','P8','O1','02']
    source_ch_labels = ['F3','F4']
    target_ch_labels = ['P3','P4']
    try:
        source_ch = [ch_labels.index(ch) for ch in source_ch_labels]
    except ValueError:
        print("Error! Required channel not found...")
    try:
        target_ch = [ch_labels.index(ch) for ch in target_ch_labels]
    except ValueError:
        print("Error! Required channel not found...")
    xv, yv = np.meshgrid(source_ch,target_ch,indexing='ij')
    ch_lst_aux = list(np.vstack((np.reshape(xv,-1),np.reshape(yv,-1))).T)
    ch_pair_lst = [[ch[0],ch[1]] for ch in ch_lst_aux if ch[0]!=ch[1]]
    
    # Alpha parameter 
    alpha = 2
    
    # Interaction time
    u_trial = (120//n)*np.ones(num_ch)
    
    # Embedding time (autocorrelation decay time)
    maxlag = (50//n)
    Tau_aux = Parallel(n_jobs=-1,verbose=0)(delayed(autocorr_decay_time)
                                            (data[ch,:],maxlag) for ch in target_ch)
    Tau = np.zeros(num_ch)
    Tau[target_ch] = Tau_aux
    # Tau = 20*np.ones(num_ch)
    
    # Embedding dimension (obtained using the cao criterion) 
    d_max = (10//n)
    Dim_aux = Parallel(n_jobs=-1,verbose=0)(delayed(cao_criterion)
                                            (data[ch,:],d_max,Tau[ch]) for ch in target_ch)
    Dim = np.zeros(num_ch)
    Dim[target_ch] = Dim_aux
    # Dim = 3*np.ones(num_ch)
    
    # Compute PAC kTE  
    kTE_cfi_aux = Parallel(n_jobs=-1,verbose=0)(delayed(kernelTransferEntropy_PAC_Ch) 
                                (data,ch_pair,Dim,Tau,u_trial,alpha,freq_ph,freq_amp,t_vec) for ch_pair in ch_pair_lst)
    kTE_matrix = np.zeros((num_ch,num_ch,num_freq_ph*num_freq_amp))
    for ii,ch_pair in enumerate(ch_pair_lst):
        kTE_matrix[ch_pair[0],ch_pair[1],:] = kTE_cfi_aux[ii].flatten() 
    kTE_mean = np.mean(kTE_matrix,axis=2)
    
    return kTE_mean


def neurofeedback_AlphaFz(data,ch_labels,fs): 
    """
    Compute the average squared alpha amplitude (Fz) for a 1 second long EEG trial (epoch).   
    
    Parameters
    ----------
    data: ndarray of shape (channels,samples)
        Input time series (number of channels x number of samples)
    ch_labels: list
        EEG channel labels 
    fs: float
        Sampling frequency (Hz)
    
    Returns
    -------
    mean_power: float
        Average squared alpha amplitude (Fz)   
    """
    # Frequency values to test
    freq = [8,10,12] # frequency of wavelet (amplitude), in Hz 
    
    # Time vector
    t_vec = 1000*np.arange(0,1,1/fs)    
    
    # Channel combination list
    target_ch_labels = ['Fz']
    try:
        target_ch = [ch_labels.index(ch) for ch in target_ch_labels]
    except ValueError:
        print("Error! Required channel not found...")
        
    # Compute amplitude
    sig_amp = Wavelet_Trial_Dec(data[target_ch,:],t_vec,freq,component ='amp')
    mean_power = np.mean(sig_amp**2)
    
    return mean_power


def compare_connectivity_CFD(cnt,cnt_baseline): 
    """
    Compare the baseline connectivity with the connectivity from a single epoch.   
    
    Parameters
    ----------
    cnt: ndarray of shape (channels,channels)
        Connectivity data from a single epoch 
    cnt_baseline: ndarray of shape (channels,channels)
        Baseline connectivity
        
    Returns
    -------
    feedback_val: float
        Feedback value for stimulus presentation [-1,1]
    """
    
    if np.mean(cnt)>np.mean(cnt_baseline):
        relative_error = np.abs(np.mean(cnt)-np.mean(cnt_baseline))/np.mean(cnt_baseline)
        feedback_val = relative_error/10
        if feedback_val>1:
            feedback_val = 1
    else:
        relative_error = -np.abs(np.mean(cnt)-np.mean(cnt_baseline))/np.mean(cnt_baseline)
        feedback_val = relative_error/10
        if feedback_val<-1:
            feedback_val = -1
    return feedback_val


def compare_connectivity_kTE(cnt,cnt_baseline): 
    """
    Compare the baseline connectivity with the connectivity from a single epoch.   
    
    Parameters
    ----------
    cnt: ndarray of shape (channels,channels)
        Connectivity data from a single epoch 
    cnt_baseline: ndarray of shape (channels,channels)
        Baseline connectivity
        
    Returns
    -------
    feedback_val: float
        Feedback value for stimulus presentation [-1,1]
    """
    relative_error = (np.mean(cnt)-np.mean(cnt_baseline))/np.mean(cnt_baseline)
    feedback_val = relative_error
    if feedback_val>1:
        feedback_val = 1
    elif feedback_val<-1: 
        feedback_val = -1
    return feedback_val


def compare_AlphaFz(sq_amp,sq_amp_baseline): 
    """
    Compare the baseline alpha squared amplitude with that of a single epoch.   
    
    Parameters
    ----------
    sq_amp: float
        Alpha squared amplitude (Fz) from a single epoch 
    cnt_baseline: float
        Baseline alpha squared amplitude (Fz)
        
    Returns
    -------
    feedback_val: float
        Feedback value for stimulus presentation [-1,1]
    """
    relative_error = (sq_amp-sq_amp_baseline)/sq_amp_baseline
    feedback_val = relative_error
    if feedback_val>1:
        feedback_val = 1
    elif feedback_val<-1: 
        feedback_val = -1
    return feedback_val
