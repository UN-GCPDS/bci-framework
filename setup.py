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

    install_requires=['simple_pid>=1.0.0',
                      'mne>=0.22.1',
                      'kafka_python>=2.0.2',
                      'tornado>=6.1',
                      'seaborn>=0.11.1',
                      'numpy>=1.20.1',
                      'matplotlib>=3.4.1',
                      'psutil>=5.8.0',
                      'cycler>=0.10.0',
                      'scipy>=1.6.2',
                      'qt_material>=2.8',
                      'browser>=0.0.1',
                      'figurestream>=1.1',
                      'gcpds>=0.1a1',
                      'openbci_stream>=1.0.0rc3',
                      'PySide2>=5.15.2',
                      'radiant>=3.1',
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



