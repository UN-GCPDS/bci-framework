BCI-Framework
=============

A distributed processing tool, stimuli delivery, psychophysiological
experiments designer and real-time visualizations for OpenBCI.

|GitHub top language| |PyPI - License| |PyPI| |PyPI - Status| |PyPI -
Python Version| |GitHub last commit| |CodeFactor Grade| |Documentation
Status|

BCI-Framework is an open-source tool for the acquisition of EEG/EMG/ECG
signals, it is developed to work with `OpenBCI’s Cyton
board <https://shop.openbci.com/products/cyton-biosensing-board-8-channel?variant=38958638542>`__,
the main core of this software lies on
`OpenBCI-Stream <https://openbci-stream.readthedocs.io/en/latest/index.html>`__,
a library that has been designed to handle all the `low-level hardware
features <https://docs.openbci.com/docs/02Cyton/CytonSDK>`__ and extend
the hardware capabilities with high-level programming libraries. An
optionally distributed paradigm for data acquisition and streaming is
available to be implemented, this approach stabilizes the sampling rate
on non-real-time acquisition systems and consists on delegate the board
handle to a dedicated environ and stream out the data in real-time.
`Write custom visualization <70-develop_visualizations.ipynb>`__ for raw
or processed time series and `design custom neurophysiological
experiments <80-develop_stimuli_delivery.ipynb>`__ are the mayor
features available in this application.

BCI-Framework consists of a graphical user interface (GUI) with a set of
individual computational processes (distributed or in a single machine),
that feed a visualization, serve a stimuli delivery, handle an
acquisition, storage data, or stream a previous one (offline analysis).
It has a built-in development environment and a set of libraries that
can be implemented by the user to create their specific functionality.

.. |GitHub top language| image:: https://img.shields.io/github/languages/top/un-gcpds/bci-framework
.. |PyPI - License| image:: https://img.shields.io/pypi/l/bci-framework
.. |PyPI| image:: https://img.shields.io/pypi/v/bci-framework
.. |PyPI - Status| image:: https://img.shields.io/pypi/status/bci-framework
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/bci-framework
.. |GitHub last commit| image:: https://img.shields.io/github/last-commit/un-gcpds/bci-framework
.. |CodeFactor Grade| image:: https://img.shields.io/codefactor/grade/github/UN-GCPDS/bci-framework
.. |Documentation Status| image:: https://readthedocs.org/projects/bci-framework/badge/?version=latest
   :target: https://bci-framework.readthedocs.io/en/latest/?badge=latest

Main Features
-------------
