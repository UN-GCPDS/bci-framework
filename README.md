> Developed by [Yeison Nolberto Cardona Álvarez](https://github.com/yeisonCardona)  
> [Andrés Marino Álvarez Meza, PhD.](https://github.com/amalvarezme)  
> César Germán Castellanos Dominguez, PhD.  
> _Digital Signal Processing and Control Group_  | _Grupo de Control y Procesamiento Digital de Señales ([GCPDS](https://github.com/UN-GCPDS/))_  
> _National University of Colombia at Manizales_ | _Universidad Nacional de Colombia sede Manizales_

----

# BCI-Framework

A distributed processing tool, stimuli delivery, psychophysiological experiments designer and real-time data visualizations for OpenBCI.

![GitHub top language](https://img.shields.io/github/languages/top/un-gcpds/bci-framework)
![PyPI - License](https://img.shields.io/pypi/l/bci-framework)
![PyPI](https://img.shields.io/pypi/v/bci-framework)
![PyPI - Status](https://img.shields.io/pypi/status/bci-framework)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bci-framework)
![GitHub last commit](https://img.shields.io/github/last-commit/un-gcpds/bci-framework)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/UN-GCPDS/bci-framework)
[![Documentation Status](https://readthedocs.org/projects/bci-framework/badge/?version=latest)](https://bci-framework.readthedocs.io/en/latest/?badge=latest)

BCI-Framework is an open-source tool for the acquisition of EEG/EMG/ECG signals, developed to work with [OpenBCI's Cyton board](https://shop.openbci.com/products/cyton-biosensing-board-8-channel?variant=38958638542), the main core of this software lies on [OpenBCI-Stream](https://openbci-stream.readthedocs.io/en/latest/index.html), a library designed to handle all the [low-level hardware features](https://docs.openbci.com/docs/02Cyton/CytonSDK) and extend the hardware capabilities with high-level programming libraries.

An optionally distributed paradigm for data acquisition and streaming is available to be implemented, this approach stabilizes the sampling rate on non-real-time acquisition systems and consists on delegate the board handle to a dedicated environ and stream out the data in real-time. [Write custom visualization](70-develop_visualizations.ipynb) for raw or processed time series and [design custom neurophysiological experiments](80-stimuli_delivery.ipynb) are the major features available in this application.

BCI-Framework comprises a graphical user interface (GUI) with a set of individual computational processes (distributed or in a single machine), that feed a visualization, serve a stimuli delivery, handle an acquisition, storage data, or stream a previous one (offline analysis). It has a built-in development environment and a set of libraries that the user can implement to create their specific functionality.

A distributed processing tool, stimuli delivery, psychophysiological experiments designer and real-time data visualizations for OpenBCI.

BCI-Framework is an open-source tool for the acquisition of EEG/EMG/ECG signals developed to work with OpenBCI’s Cyton board. The main core of this software lies on OpenBCI-Stream, a library designed to handle all the low-level hardware features and extend the hardware capabilities with high-level programming libraries. A distributed paradigm for data acquisition and streaming is available to be implemented. This approach stabilizes the sampling rate on non-real-time acquisition systems and consists on delegate the board handle to a dedicated environ and stream out the data in real-time. Write custom visualization for raw or processed time series and design custom neurophysiological experiments are the major features available in this application.

In particular BCI-Framework comprises a graphical user interface (GUI) with a set of individual computational processes (distributed or in a single machine). Also, this application can feed a visualization, serve a stimuli delivery, handle an acquisition, storage data, or stream a previous one (offline analysis). Finally, it integrates a built-in development environment and a set of libraries that the user can implement to create their specific functionality.

## Screenshots

![](https://github.com/UN-GCPDS/bci-framework/blob/master/docs/source/notebooks/images/readme.gif)
