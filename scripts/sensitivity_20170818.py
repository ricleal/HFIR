# pylint: disable=line-too-long,C0103
from __future__ import print_function
'''

This script can be used for generation of the flood files
(creates a sensitivity file)

Done and tested with Lisa on 2017/08/18

'''
import os
import mantid
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.hfir_command_interface import *

import sys
sys.path.append("/HFIR/CG2/shared/scripts/lib")
from file_helper import CG2

# Set IPTS and Exp number
cg2 = CG2(828, 206)

# We have 3 flood files at different translations
flood_field_raw = cg2.filepath(17, 1)

# We have 3 respective centers
flood_field_center = cg2.filepath(16, 1)

# Dark flood
dark_flood = cg2.filepath(38, 1)

# Creates a folder in shared
output_folder = "/tmp"
output_file = os.path.join(output_folder, "sensitivity.nxs")

GPSANS()
DirectBeamCenter(flood_field_center)
SolidAngle(detector_tubes=True)
DarkCurrent(dark_flood)
MonitorNormalization()

# This is used to to setup the reduction process with the options above.
ReductionSingleton().pre_process()

# From here are just usual Mantid Algorithms
SANSSensitivityCorrection(
    Filename=flood_field_raw,
    UseSampleDC=False,
    DarkCurrentFile=dark_flood,
    # You may need to edit this!!
    # MinEfficiency too high masks the tubes!
    # See the output workspace
    MinEfficiency=0.5,
    MaxEfficiency=1.7,
    OutputSensitivityWorkspace="sensitivity_raw",
    ReductionProperties=ReductionSingleton().property_manager
)

# Let's clone the calculated workspace so we can draw mask in one of them
CloneWorkspace(
    InputWorkspace='sensitivity_raw',
    OutputWorkspace='masked'
)

#
# MASK `masked` workspace by HAND in MantidPlot
# --------------------
# Open the Instrument View for the `masked` workspace.
# Draw a circle around the beamstop and the top and bottom of the detector
# Then do: Apply to Data
#

# Once you have apply the masks zones the data in the `masked` workspace do:
SANSPatchSensitivity(
    InputWorkspace='sensitivity_raw',
    PatchWorkspace='masked',
    DegreeofThePolynomial=3
)

# Save the the sensitivity RAW. This file is then used in the regular
# SANS Reduction algorithms
SaveNexus(
    InputWorkspace='sensitivity_raw',
    Filename=output_file
)
