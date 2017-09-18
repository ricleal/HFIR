# pylint: disable=line-too-long,C0103
from __future__ import print_function

import json
import os
import sys

sys.path.append("/HFIR/CG2/shared/scripts/lib")
import mantid
from file_helper import CG2, Names
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.hfir_command_interface import *

'''
Script for Bin

Scattering composed of multiple files summed to improve statistics:
- Using `range_nested`

It used flood from Lisa
Needs Bin approval!

'''

#
# INITS
#

# Set IPTS and Exp number
cg2 = CG2(19748, 240)


# Input scan numbers
sample_scattering_list = cg2.range_nested([11,13,14],["1-3",1,1])
background_scattering_list = cg2.repeat(17,1, 3)

sample_transmission_list = cg2.repeat(19,1, 3)
background_transmission_list = cg2.repeat(18,1, 3)

# Thickness of the cell (unit = cm)
thickness_list = [0.2]*3

# Empty Beam Transmission 
empty_transmission_filename = cg2.filepath(20,1)

# Beam Center for this configuration
beam_center_filename = cg2.filepath(20,1)


# MACHINE PHYSICS FILES
flood_field_filename =  os.path.join( CG2(828, 206).shared('Ricardo'), "sensitivity.nxs")

#Blocked Beam in Your Experiment
dark_filename = "/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0021_0001.xml"

#
# You should't need to edit below this part!
#

# read masked_ids
with open('/HFIR/CG2/shared/scripts/masked_pixel_ids.json', 'r') as f:
    masked_pixel_ids = json.load(f)

# Output folder
data_out_folder = cg2.shared("Ricardo")

# Make sure the input lists have all the same size:
input_lists = [
    sample_scattering_list,
    background_scattering_list,
    sample_transmission_list,
    background_transmission_list,
    thickness_list
]
assert all(len(x) == len(input_lists[0]) for x in input_lists), \
    "All input lists must be the same size!"

#
# Main cycle
#
root_path = cg2.datafiles
logger.notice("Starting reduction...")

# Let's iterate over all filenames
for (sample_scattering,
     background_scattering,
     sample_transmission,
     background_transmission,
     thickness) in zip(input_lists):

    # get filename from /a/b/c/filename.ext
    ws_name = Names(sample_scattering).parse()
    logger.notice("-"*80)
    logger.notice("MAIN Output Filename:    {:>40}".format(ws_name))
    logger.notice("Trans Data Filename:     {:>40}".format(os.path.basename(sample_transmission)))
    logger.notice("Scatt Data Filename:     {:>40}".format(os.path.basename(sample_scattering) if isinstance(sample_scattering, str) else sample_scattering))
    logger.notice("Bkg Trans Data Filename: {:>40}".format(os.path.basename(background_transmission)))
    logger.notice("Bkg Scatt Data Filename: {:>40}".format(os.path.basename(background_scattering)))

	#
    #  Reduction
    #

    GPSANS()
    SetAbsoluteScale(factor=.00021)
    DataPath(cg2.datafiles)
    DirectBeamCenter(beam_center_filename)
    SolidAngle(detector_tubes=True)
    DarkCurrent(dark_filename)
    MonitorNormalization()
    Mask(nx_low=0, nx_high=0, ny_low=20, ny_high=20, component_name="detector1")
    MaskDetectors(masked_pixel_ids)
    MaskDetectorSide(side_to_mask="Back")
    # SensitivityCorrection(flood_field_filename, min_sensitivity=0.3, max_sensitivity=1.7,
    #     dark_current=sensitivity_dark_current, use_sample_dc=True)
    SensitivityCorrection(flood_field_filename, min_sensitivity=0.1, max_sensitivity=1.5, use_sample_dc=False)
    DivideByThickness(thickness)
    DirectBeamTransmission(sample_transmission, empty_transmission_filename,
        beam_radius=3, theta_dependent=True, use_sample_dc=True)
    TransmissionDarkCurrent(dark_filename)
    AppendDataFile(sample_scattering, workspace=ws_name)
    AzimuthalAverage(n_bins=100, n_subpix=1, log_binning=False, align_log_with_decades=True, error_weighting=True)
    IQxQy(nbins=80)
	#BACKGROUND SETUP
    Background(background_scattering)
    BckDirectBeamTransmission(background_transmission, empty_transmission_filename, beam_radius=3,theta_dependent = True)
    BckTransmissionDarkCurrent(dark_filename)
    #OUTPUT SETUP
    OutputPath(data_out_folder)
    SaveIq()
    Reduce()

    #
    # Done
    #
    logger.notice("Finished: {}".format(sample_scattering))
