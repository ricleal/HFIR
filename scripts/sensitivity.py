# pylint: disable=line-too-long,C0103
from __future__ import print_function
'''

This script can be used for generation of the flood files

'''
import os
import mantid
from mantid.simpleapi import *
from reduction_workflow.instruments.sans.hfir_command_interface import *

import sys
sys.path.append("/HFIR/CG2/shared/scripts/lib")
from file_helper import CG2

# Set IPTS and Exp number
cg2 = CG2(828, 184)

flood_field_file_raw = cg2.filepath(45,1)
# flood_field_file_raw = cg2.filepath(47,1)
# flood_field_file_raw = cg2.filepath(49,1)

flood_field_file_patched = "/HFIR/CG2/shared/floods/sensitivity_patched_dt1_6.8m.nxs"
# flood_field_file_patched = "/HFIR/CG2/shared/floods/sensitivity_patched_dt200_6.8m.nxs"
# flood_field_file_patched = "/HFIR/CG2/shared/floods/sensitivity_patched_dt400_6.8m.nxs"

Load(Filename=flood_field_file_raw,OutputWorkspace='ws1')
CloneWorkspace(InputWorkspace='ws1',OutputWorkspace='masked')

#
# Mask HERE By HAND!!!
# Draw a circle around the beamsop in instrument view
# for the mask workspace. Then do: Apply to Data
#
SANSPatchSensitivity(InputWorkspace='ws1',PatchWorkspace='masked',
                     ComponentName='detector1',DegreeofThePolynomial=4)
SaveNexus(InputWorkspace='ws1', Filename=flood_field_file_patched)

