# PREFIRE_MSK

Python package to produce the PREFIRE 2B-MSK product. This product contains a cloud mask for each PREFIRE TIRS FOV.

This code is released under the terms of this [LICENSE](LICENSE).  The version of this package can be found in [VERSION.txt](VERSION.txt).

# Installation

## Requirements

Python version 3.6+ is required, along with the following third-party Python
packages: numpy, netcdf4, xarray, tensorflow

The associated (Python-based) git repositories ['PREFIRE_tools'](https://github.com/UW-PREFIRE/PREFIRE_tools), ['PREFIRE_PRD_GEN'](https://github.com/UW-PREFIRE/PREFIRE_PRD_GEN), and ['PREFIRE_ML_MSK'](https://github.com/UW-PREFIRE/PREFIRE_ML_MSK) are also required for the proper operation of this package.

## Python Environment Setup

It is recommended to install the above Python packages in a dedicated conda environment (or something similar).  The packages used (and their versions) can be found in [conda_env.list](conda_env.list).

For example, using conda (and specifying Python 3.10.x from the conda-forge channel):

```
conda create --name for_PREFIRE_MSK -c conda-forge python=3.10;
conda activate for_PREFIRE_MSK;
conda install -c conda-forge numpy netcdf4 xarray tensorflow=2.14;
```

The location of 'PREFIRE_PRD_GEN', 'PREFIRE_ML_MSK', and 'PREFIRE_tools' depends on the value of the user's PYTHONPATH and/or sys.path -- for example, one could simply add each of those git repositories' local root Python source code directory to PYTHONPATH.

Operationally, however, this package uses symbolic links to those git repositories' local root Python source code directories (or full copies of the same) in the source/ directory.  To use the symlink method (assuming that all PREFIRE code repositories are in the same parent directory, and that the PYTHONPATH environment variable is unset or empty):

```
cd source;
ln -s ../../PREFIRE_PRD_GEN/source/PREFIRE_PRD_GEN PREFIRE_PRD_GEN;
ln -s ../../PREFIRE_tools/source/python/PREFIRE_tools PREFIRE_tools;
ln -s ../../PREFIRE_ML_MSK/source/PREFIRE_ML_MSK PREFIRE_ML_MSK;
```

## Environment Variables

### Each job (executing this science algorithm package) is configured via information contained within environment variables.

### To specify that numpy, scipy, et cetera used by this algorithm should not use more than one thread or process, the below environment variables are expected to be set:

```
MKL_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1
OMP_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
OPENBLAS_NUM_THREADS=1
```

### Some environment variables are always required to be set (also see test/run.sh):

PACKAGE_TOP_DIR  :  the top-level directory (i.e., the one that contains dist/, test/, etc.) of this package

ANCILLARY_DATA_DIR  :  the package's ancillary data directory (should be an absolute path)

OUTPUT_DIR  :  the directory in which all meaningful output will be written (should be an absolute path)

ATRACK_IDX_RANGE_0BI  :  coded frame (i.e., along-track segment) subset to process and output, for example: "ATRACK_IDXRANGE_0BASED_INCLUSIVE:2001:3100" (atrack dimension indices from 2001 through 3100) "ATRACK_IDXRANGE_0BASED_INCLUSIVE:0:END" (atrack dim indices from 0 through the last frame)

L1B_RAD_FILE  :  filepath of the "source" 1B-*RAD product granule (should be an absolute path)

AUX_MET_FILE  :  filepath of the input AUX-MET product granule (should be an absolute path)

### Some environment variables may not need to be set for operational use (instead, some have corresponding hard-coded default values that are "baked into" each operational algorithm delivery), but exist to enable efficient development and testing (also see test/run.sh):

PRODUCT_FULLVER  :  the full product processing/revision version string (e.g., "R01_P00").  Only increment 'Rxx' when the resulting products will be DAAC-ingested.

For the cloud mask algorithm based on neural networks, the required pretrained neural network files are in directories named <NN_model_moniker>-SATx-<NN_model_subv>/, and the environment variables below can be used together to specify which directory will be used:

NN_MODEL_MONIKER  :  general moniker of a particular NN training series (e.g., "v12_SRF_noiseless")

NN_MODEL_SUBV  :  the subversion of a particular NN training series (e.g., "01")

# Running the test script(s)

## Obtain and unpack any ancillary data

Various additional ancillary data files are needed for this software package.  A zip-archive file containing that data can be downloaded from [here](https://zenodo.org/records/17081025).

To install the downloaded ancillary data:

(1) If needed, copy the downloaded zip-archive file to the `dist/` subdirectory within this software package.  Then change directory to that same `dist/` subdirectory within this software package.

(2) Extract (unzip) the downloaded zip-archive file, which should automatically put the extracted files into the `ancillary/` subdirectory.

## Prepare the test input and output directories:

`cd test;`

On Linux/UNIX systems, possibly create a useful symbolic link to the test input data (if needed):

`ln -s WHEREEVER_THE_DATA_IS/inputs inputs;`

Prepare the output directory (Linux/UNIX example):

`mkdir -p outputs;`

_OR_ perhaps something like

`ln -s /data/users/myuser/data-PREFIRE_MSK/outputs outputs;`

## Run the MSK package

### A Linux/UNIX example

`cp run.sh my-run.sh;`

Edit `my-run.sh` as needed (e.g., change input file names)

`./my-run.sh`

The output file(s) will be in `test/outputs/`

### _The creation of this code was supported by NASA, as part of the PREFIRE (Polar Radiant Energy in the Far-InfraRed Experiment) CubeSat mission._
