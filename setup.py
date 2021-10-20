import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
version_str = open(os.path.join(
    'bci_framework', '_version.txt'), 'r').read().strip()
setup(
    name='bci-framework',
    version=version_str,
    packages=['bci_framework'],

    author='Yeison Cardona',
    author_email='yencardonaal@unal.edu.co',
    maintainer='Yeison Cardona',
    maintainer_email='yencardonaal@unal.edu.co',

    download_url='https://github.com/UN-GCPDS/bci_framework',

    install_requires=['cycler',
                      'matplotlib',
                      'kafka_python',
                      'tornado',
                      'scipy',
                      'qt-material',
                      'numpy',
                      'mne',
                      'psutil',
                      'simple_pid',
                      'figurestream',
                      'gcpds',
                      'openbci_stream',
                      'PySide2',
                      'radiant',
                      'psutil',
                      ],

    include_package_data=True,
    license='BSD-2-Clause',
    description="A real-time tool for acquisition, analysis and stimuli delivery for OpenBCI.",

    long_description=README,
    long_description_content_type='text/markdown',

    python_requires='>=3.8',

    entry_points={
        'console_scripts': ['bci-framework=bci_framework.__main__:main'],
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Embedded Systems',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],

)



