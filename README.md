This is a testing branch for jcpds5 development
----------

The main new feature of the jcpds5 format is that it allows to describe the PVT EOS using different formulations, either existing or user defined. 

The new version of the commonly used jcpds file format, called here V5, includes two new tags: 'Z' and 'EOS'. Z is the nubmber of formula units per unit cell. 'Z' tag is needed by many equation of state formulations that are based on molar volume rather than unit cell volume. 'EOS' tag includes a dict string that bundles multiple parameters that descrive a particular equation of state. Here we use the same formulation for the EOS dict string as the "Burnman" package (https://github.com/geodynamics/burnman). For details about the EOS dict string, please refer to the "Burnman" package documentation. An equation of states file (eos_definitions.py) provides descriptions for different equations of state that are supported. This file is also used by the widget constructor to create a eos widget with appropriate fields. The eos_definitions.py can be modified to include any number of new formulations. When adding a new equation of state, that is not included in the Burnman package, we have to create a new class that overrides the general EquationOfState class in Burnman, add a new description in eos_definitions.py and add a hook for the constructor of the new EOS class it in jcpds.py. 

Moreover, a new version of the JcpdsEditorWidget now shows a drop-down box that allows the user to choose an EOS form to use.

Overall, several existing Dioptas modules have been modified to make them compatible with the new EOS calculation approach:<br>
model/util/: PhaseModel.py, jcpds.py <br>
model/: DioptasModel.py<br>
controller/integration/phase/: JcpdsEditorController.py<br>
widtegs/integration/: JcpdsEditorWidget.py<br>

And, some new items have been added:<br>
burnman package: burnman folder currently copied to the same location as dioptas folder<br>
model/util/: birch_murnaghan_thermal.py, eos_definitions.py<br>

Some examples of the jcpds files are provided for testing purposes:
Dioptas/dioptas/tests/data/jcpds/: mgo_V5_(eos_slb2).jcpds, au_Anderson_V5_(eos_jcpds4).jcpds


Dioptas
======

A GUI program for fast analysis of powder X-ray diffraction Images. It provides the capability of calibrating, 
creating masks, having pattern overlays and showing phase lines.

Maintainer
----------

Clemens Prescher (clemens.prescher@gmail.com)

Requirements
------------
    * python 3.4-3.7
    * qtpy with PyQt5/PyQt4/PySide
    * numpy
    * scipy
    * future
    * pyFAI (https://github.com/silx-kit/pyFAI)
    * fabio (https://github.com/silx-kit/fabio)
    * pyqtgraph (https://github.com/pyqtgraph/pyqtgraph
    * scikit-image
    * PyCifRw

<b>optional:</b>

    * pyopencl (increasing pyFAI integration speed)
    * fftw3 (increasing pyFAI instegration speed)

It is known to run on Windows, Mac and Linux. For optimal usage on a windows machine it should be run with 64 bit
python. When used with 32 bit Dioptas occasionally crashes because of limited memory allocation possibilities.

Installation
------------

### Executables

Executable versions for Windows, Mac OsX and Linux (all 64bit) can be downloaded from:

https://github.com/Dioptas/Dioptas/releases

The executable versions are self-contained folders, which do not need any python installation.

### Code

In order to make changes to the source code yourself or always get the latest development versions you need to install
the required python packages on your machine.

The easiest way to install the all the dependencies for Dioptas is to use the Anaconda (or miniconda) 64bit Python 3 distribution.
Please download it from https://www.continuum.io/downloads. After the installer added the scripts to your path (or use the
Anaconda prompt on windows) please run the following commands on the commandline:

```bash
conda install --yes dioptas pyfai -c cprescher
```

and then run Dioptas by typing:
```bash
dioptas
```
in the commandline.


Running the Program from source
-------------------------------

You can start the program by running the Dioptas.py script in the dioptas folder:

```bash
python Dioptas.py
```
