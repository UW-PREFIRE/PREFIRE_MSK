"""
Retrieve a cloud mask from input PREFIRE TIRS Level-1B and AUX-MET files.

This program requires Python version 3.6 or later, and is importable as a 
Python module.
"""

  # From the Python standard library:
from pathlib import Path
import os
import sys
import argparse
import subprocess

  # From other external Python packages:

  # Custom utilities:


#--------------------------------------------------------------------------
def main(anchor_path):
    """Driver routine."""

    sys.path.append(os.path.join(anchor_path, "..", "source"))
    from PREFIRE_MSK.create_MSK_product import create_MSK_product

#    this_environ = os.environ.copy()

    this_dir = Path(anchor_path)  # typically the 'dist' directory
    ancillary_dir = os.environ["ANCILLARY_DATA_DIR"]
    input_L1B_fpath = os.environ["L1B_RAD_FILE"]
    input_AUX_MET_fpath = os.environ["AUX_MET_FILE"]
    output_dir = os.environ["OUTPUT_DIR"]

    more_cfg = {}
    try:
        more_cfg["pretrained_NN_moniker"] = os.environ["NN_MODEL_MONIKER"]
        more_cfg["pretrained_NN_subv"] = os.environ["NN_MODEL_SUBV"]
    except:
        more_cfg["pretrained_NN_moniker"] = None
        more_cfg["pretrained_NN_subv"] = None

    atrack_idx_range_str = os.environ["ATRACK_IDX_RANGE_0BI"]
    tokens = atrack_idx_range_str.split(':')
    if tokens[2] == "END":
        atrack_np_idx_range = ("atrack", int(tokens[1]), None)  # Numpy indexing
    else:
        atrack_np_idx_range = ("atrack", int(tokens[1]),
                               int(tokens[2])+1)  # Numpy indexing

      # Default product_fullver:
    if "PRODUCT_FULLVER" not in os.environ:
        product_full_version = "R01_P00"
    elif len(os.environ["PRODUCT_FULLVER"].strip()) == 0:
        product_full_version = "R01_P00"
    else:
        product_full_version = os.environ["PRODUCT_FULLVER"]

    # Create the product data:
    create_MSK_product(input_L1B_fpath, input_AUX_MET_fpath, output_dir,
                       product_full_version, more_cfg, artp=atrack_np_idx_range)


if __name__ == "__main__":
    # Determine fully-qualified filesystem location of this script:
    anchor_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    # Process arguments:
    arg_description = ("Retrieve a cloud mask from input PREFIRE TIRS Level-1B "
                       "and AUX-MET files.")
    arg_parser = argparse.ArgumentParser(description=arg_description)

    args = arg_parser.parse_args()

    # Run driver:
    main(anchor_path)
