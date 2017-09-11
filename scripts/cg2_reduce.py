# pylint: disable=line-too-long,C0103
from __future__ import print_function
'''

'''
import os
import mantid
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.hfir_command_interface import *

import sys
sys.path.append("/HFIR/CG2/shared/scripts/lib")
from file_helper import CG2

'''

EXAMPLE

'''

#
# INITS
#

# Set IPTS and Exp number
cg2 = CG2(18381, 180)

# Input scan numbers
sample_scattering_list = cg2.range(45,1)
background_scattering_list = cg2.range(80,1)

sample_transmission_list = cg2.range(15,1)
background_transmission_list = cg2.range(4,1)

thickness_list =  [0.1]

# Empty Beam Transmission 
empty_transmission_filename = cg2.filepath(16,1)

# Beam Center
beam_center_filename = cg2.filepath(45,1)

# MACHINE PHYSICS FILES
main_flood_filename =  CG2(828,165).filepath(8,1)
dark_filename = CG2(18381,180).filepath(46,1)
sensitivity_dark_current =  CG2(18381,180).filepath(40,1)

#
# You don't need to edit below this part!
#

# Output folder
data_out_folder = cg2.shared("Reduced")

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
     thickness) in zip(sample_scattering_list,
                       background_scattering_list,
                       sample_transmission_list,
                       background_transmission_list,
                       thickness_list):

    # get filename from /a/b/c/filename.ext
    ws_main_name = os.path.basename( os.path.splitext(sample_scattering)[0])

    logger.notice("MAIN Output Filename:    {:>40}".format(ws_main_name))
    logger.notice("Trans Data Filename:     {:>40}".format(os.path.basename(sample_transmission)))
    logger.notice("Scatt Data Filename:     {:>40}".format(os.path.basename(sample_scattering)))
    logger.notice("Bkg Trans Data Filename: {:>40}".format(os.path.basename(background_transmission)))
    logger.notice("Bkg Scatt Data Filename: {:>40}".format(os.path.basename(background_scattering)))

	#
    # Main reduction
    #

    GPSANS()
    #SetAbsoluteScale(factor=1.0)
    DataPath(cg2.datafiles)
    DirectBeamCenter(beam_center_filename)
    SolidAngle(detector_tubes=True)
    DarkCurrent(dark_filename)
    MonitorNormalization()
    Mask(nx_low=0, nx_high=0, ny_low=20, ny_high=20, component_name="detector1")
    MaskDetectorSide(side_to_mask="Front")
    SensitivityCorrection(main_flood_filename, min_sensitivity=0.3, max_sensitivity=1.7,
        dark_current=sensitivity_dark_current, use_sample_dc=True)
    DivideByThickness(thickness)
    DirectBeamTransmission(sample_transmission, empty_transmission_filename,
        beam_radius=3, theta_dependent=True, use_sample_dc=True)
    TransmissionDarkCurrent(dark_filename)
    AppendDataFile(sample_scattering, workspace=ws_main_name)
    AzimuthalAverage(n_bins=100, n_subpix=1, log_binning=True, align_log_with_decades=True, error_weighting=True)
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
