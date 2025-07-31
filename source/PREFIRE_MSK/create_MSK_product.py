"""
Create MSK Level-2B product corresponding to a PREFIRE Level-1B file.

This program requires Python version 3.6 or later, and is importable as a
Python module.
"""

  # From the Python standard library:
import sys
import os
import errno
import datetime

  # From other external Python packages:
import netCDF4

  # Custom utilities:
from PREFIRE_PRD_GEN.file_creation import write_data_fromspec
from PREFIRE_PRD_GEN.file_read import load_all_vars_of_nc4group, \
                                      load_all_atts_of_nc4group
import PREFIRE_MSK.filepaths as MSK_fpaths
from PREFIRE_ML_MSK.ML_MSK import run_ML_cmask
import PREFIRE_ML_MSK.filepaths as ML_MSK_fpaths


#--------------------------------------------------------------------------
def mkdir_p(path):
    """Emulates 'mkdir -p' functionality."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


#--------------------------------------------------------------------------
def create_MSK_product(L1B_fpath, AUX_MET_fpath, output_dir,
                       product_full_version, more_cfg, artp=("atrack",0,None)):
    """
    Main function to create MSK Level-2 product from input Level-1B and
     AUX-MET files.

    Parameters
    ----------
    L1B_fpath : str
        Path to Level-1B file.
    AUX_MET_fpath : str
        Path to AUX-MET file.
    output_dir : str
        Directory to which MSK Level-2 NetCDF-format file(s) will be written.
    product_full_version : str
        Full product version ID (e.g., "Rzz_Pxx").
    more_cfg : dict
        Dictionary containing any further configuration info
    artp : 3-tuple (str, int, int)
        (optional) atrack range to process, a 3-tuple containing the dimension
         name to subset, and start and stop indices (NumPy indexing convention)
         in the given granule

    Returns
    -------
    None.
    """

    work_dir = output_dir
    product_specs_fpath = os.path.join(MSK_fpaths.package_ancillary_data_dir,
                                       "Msk_product_filespecs.json")

    # Calculate stuff:
       
    with netCDF4.Dataset(L1B_fpath, 'r') as L1B_ds:
        sensor_ID_str = L1B_ds.sensor_ID[-1]
        n_xtrack = L1B_ds.dimensions["xtrack"].size

    # These values are the current operationally-nominal ones, and will be used
    #  unless the environment variables NN_MODEL_MONIKER and NN_MODEL_SUBV are
    #  set:
    if sensor_ID_str == '1':  # SAT1
        pt_NN_moniker, pt_NN_subv = ("VIIRS", "03")
    else:  # SAT2
        pt_NN_moniker, pt_NN_subv = ("VIIRS", "05")

    if more_cfg["pretrained_NN_moniker"] is not None:
        pt_NN_moniker = more_cfg["pretrained_NN_moniker"]
    if more_cfg["pretrained_NN_subv"] is not None:
        pt_NN_subv = more_cfg["pretrained_NN_subv"]

    training_version = "{}-SAT{}-{}".format(pt_NN_moniker, sensor_ID_str,
                                            pt_NN_subv)
    tmp_path = os.path.join(MSK_fpaths.package_ancillary_data_dir,
                            training_version)
    NN_model_fpaths = ([os.path.join(tmp_path,
               f"SAT{sensor_ID_str}_xscene{x+1:1d}") for x in range(n_xtrack)])

    dat_NN = run_ML_cmask(L1B_fpath, AUX_MET_fpath,
                          NN_model_fpaths, output_dir, n_xtrack,
                          return_rather_than_write_dat=True)

    # Collect/determine fields to be output:

    dat = {}
    dat["Msk"] = {}
    global_atts = {}

    with netCDF4.Dataset(L1B_fpath, 'r') as L1B_ds:
        # Load "Geometry" group and its group attributes from the Level-1B file:
        dat["Geometry"] = load_all_vars_of_nc4group("Geometry", L1B_ds, artp)
        dat["Geometry_Group_Attributes"] = (
                            load_all_atts_of_nc4group("Geometry", L1B_ds))

        atdim_full = L1B_ds.dimensions[artp[0]].size

        global_atts["granule_ID"] = L1B_ds.granule_ID

        global_atts["spacecraft_ID"] = L1B_ds.spacecraft_ID
        global_atts["sensor_ID"] = L1B_ds.sensor_ID
        global_atts["ctime_coverage_start_s"] = L1B_ds.ctime_coverage_start_s
        global_atts["ctime_coverage_end_s"] = L1B_ds.ctime_coverage_end_s
        global_atts["UTC_coverage_start"] = L1B_ds.UTC_coverage_start
        global_atts["UTC_coverage_end"] = L1B_ds.UTC_coverage_end
        global_atts["orbit_sim_version"] = L1B_ds.orbit_sim_version
        global_atts["SRF_NEdR_version"] = L1B_ds.SRF_NEdR_version

    # Update with ML_MSK (NN) results:
    dat["Msk"].update(dat_NN["Msk"])

    dat["Msk_Group_Attributes"] = {"cldmask_training_version": training_version}

    with open(MSK_fpaths.scipkg_prdgitv_fpath, 'r') as in_f:
        line_parts = in_f.readline().split('(', maxsplit=1)
        global_atts["provenance"] = "{}{} ( {}".format(line_parts[0],
                                                       product_full_version,
                                                       line_parts[1].strip())

    with open(MSK_fpaths.scipkg_version_fpath) as f:
        global_atts["processing_algorithmID"] = f.readline().strip()

    L1B_fn = os.path.basename(L1B_fpath)
    in_file_l = [L1B_fn, os.path.basename(AUX_MET_fpath)]
    global_atts["input_product_files"] = ", ".join(in_file_l)

    global_atts["full_versionID"] = product_full_version
    global_atts["archival_versionID"] = (
                           product_full_version.split('_')[0].replace('R', ''))
    global_atts["netCDF_lib_version"] = netCDF4.getlibversion().split()[0]

    # Generate MSK output file name:
    tokens = L1B_fn.split('_')
    fname_tmp = "PREFIRE_SAT{}_2B-MSK_{}_{}_{}.nc".format(
               global_atts["spacecraft_ID"][-1], global_atts["full_versionID"],
               tokens[5], global_atts["granule_ID"])
    if (artp[1] == 0) and (artp[2] is None or artp[2] == atdim_full-1):
        MSK_fname = "raw-"+fname_tmp
    else:
        if artp[2] is None:
            tmp_idx = atdim_full-1
        else:
            tmp_idx = artp[2]-1
        MSK_fname = "raw-"+fname_tmp[:-3]+ \
              f"-{artp[0]}_{artp[1]:05d}_{tmp_idx:05d}_of_{atdim_full:05d}f.nc"
    global_atts["file_name"] = MSK_fname

    now_UTC_DT = datetime.datetime.now(datetime.timezone.utc)
    global_atts["UTC_of_file_creation"] = now_UTC_DT.strftime(
                                                        "%Y-%m-%dT%H:%M:%S.%f")

      # Add global attributes to output dictionary:
    dat["Global_Attributes"] = global_atts

    MSK_fpath = os.path.join(output_dir, MSK_fname)
    mkdir_p(os.path.dirname(MSK_fpath))

    # Use generic PREFIRE product writer to produce the MSK output file:
    write_data_fromspec(dat, MSK_fpath, product_specs_fpath, verbose=True)
