"""
Core File for EBR-II Model

Author: LZK
Date: 2023-1-26
Project: Verification of LoongSARAX Program

File Log:
2023-1-26   File created
2023-1-28   Basic structure created
"""
import os
import sys
from getpass import getuser

PYSARAX_PATH = {
    '12247': 'G:\Research\Research\Projects\LoongSARAXVerif\code\pySARAX\lib', 
    'Zikang Li': 'C:\\SJTUGraduate\\Research\\Projects\\LoongSARAXVerif\\code\\pySARAX\\lib',
    'admin':  'C:\\SJTUGraduate\\Research\\Projects\\LoongSARAXVerif\\code\\pySARAX'
}
sys.path.append(PYSARAX_PATH[getuser()])

import pandas as pd
from pySARAX import Core
from assemblies import *

# ###################################################
#                  Auxiliary Function
# ###################################################
assembLocPath = "C:\SJTUGraduate\Research\Projects\LoongSARAXVerif\code\model_ver2\\assembLocations.xlsx"
assembLoc = pd.read_excel(assembLocPath)

def buildLattice() -> list:
    """
    Build the core lattice of EBR-II
    """
    assembNum = lambda r: 6 * r if r > 0 else 1
    lattice = []

    for r in range(16):
        ring = []
        for k in range(assembNum(r)):
            MKType = 'MKII'
            location = slugmat.convertLocation((r, k))
            targetAssemb = assembLoc[assembLoc['Location'] == location]

            # Fill the blank location at margin
            if targetAssemb.empty:
                assembType = 'blank'
            else:
                assembType = typeNameTable[targetAssemb['Type'].item()]

            # Rename the driver
            if 'MK' in assembType and int(targetAssemb['Number']) in halfWorthDrivers:
                assembType = 'HWD'
            elif assembType == 'MKII':
                assembType = 'driver'
            elif assembType == 'MKIIA':
                assembType = 'driver'
                MKType = 'MKIIA'
            
            assembly = buildAssemb(assembType, location, MKType)
            if assembType == 'Safeties':
                print(r, k, location, targetAssemb)
            ring.append(assembly)
            print("Assembly [{}, {}, {}] created.".format((r+1, k+1), location, assembType))

        lattice.append(ring)
        print("Ring [{:d}] created.".format(r+1))
    
    return lattice


# ###################################################
#                        Core
# ###################################################
core = Core(name='EBR-II', ring=16, pitch=5.8929, coolant=blankSec)

# Lattice Geometry & Materials
# core.lattice = [
#     [buildAssemb('dummy', '05C03', 'MKIIA')],
#     [drivers['test-MKIIA'].copy(typeName='driver-MKIIA', location='test') for _ in range(6)],
#     [blankAssemb for _ in range(12)]
# ]

core.lattice = buildLattice()

# Control Parameters
core.power = 62.5E6 # Wth
core.gammaHeat = True
core.boundaryConditions = (0, 0) # 0: vacuum, 1: reflect

# Meshing & Ploting
core.complete()

core.meshing(tolerance=0.1000)

# Plot
cwd = os.getcwd()
core.plotRaial(savePath=os.path.join(cwd, 'output', 'radial.svg'))
core.plotAxial(savePath=os.path.join(cwd, 'output', 'axial.svg'))

# Generate Input Cards
cwd = os.getcwd()
tulipPath = os.path.join(cwd, 'output', "TPmate.inp")
lavenderPath = os.path.join(cwd, 'output', "lavender.inp")

# with open(tulipPath, 'w', encoding='utf-8') as tulip:
#     tulip.write(core.toTULIP())

# with open(lavenderPath, 'w', encoding='utf-8') as lavender:
#     lavender.write(core.toLAVENDER())
