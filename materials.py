"""
Materials File for EBR-II Model

Author: LZK
Date: 2023-1-22
Project: Verification of LoongSARAX Program

File Log:
2023-1-22   File created
2023-1-23   General Materials completed;
            Class SlugMat created
2023-1-25   Class SlugMat completed
2023-2-1    Add some materials of HWCR & safety
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
from numpy import pi
from pySARAX import Material

# ######################################################################
#                         General Materials
# 
# The data of materials in this section come from the file EBR-II.pdf, 
# which do NOT change among assemblies. 
# ######################################################################

bulkTemp = 616.0 # K, bulk temperature

sodium = Material(name='sodium')
sodium.addElement(element='Na', density=2.478e-2, temperature=bulkTemp)

ss316 = Material(name='SS316')
ss316.addElement(element='C', density=3.209e-4, temperature=bulkTemp)
ss316.addElement(element='Si', density=1.715e-3, temperature=bulkTemp)
ss316.addElement(element='Cr', density=1.714e-2, temperature=bulkTemp)
ss316.addElement(element='Mn', density=3.725e-4, temperature=bulkTemp)
ss316.addElement(element='Fe', density=5.643e-2, temperature=bulkTemp)
ss316.addElement(element='Ni', density=9.850e-3, temperature=bulkTemp)
ss316.addElement(element='Mo', density=1.256e-3, temperature=bulkTemp)

plenumGas = Material(name='plenum gas')
plenumGas.addElement(element='He', density=6.540e-5, temperature=bulkTemp)
plenumGas.addElement(element='Ar', density=2.189e-6, temperature=bulkTemp)

ss304 = Material(name='SS304')
ss304.addElement(element='C', density=2.759e-4, temperature=bulkTemp)
ss304.addElement(element='Si', density=8.428e-4, temperature=bulkTemp)
ss304.addElement(element='P', density=1.681e-5, temperature=bulkTemp)
ss304.addElement(element='S', density=8.858e-6, temperature=bulkTemp)
ss304.addElement(element='Cr', density=1.698e-2, temperature=bulkTemp)
ss304.addElement(element='Mn', density=6.549e-4, temperature=bulkTemp)
ss304.addElement(element='Fe', density=6.024e-2, temperature=bulkTemp)
ss304.addElement(element='Ni', density=7.219e-3, temperature=bulkTemp)

upperExten = Material(name='upper extension')
upperExten.addElement(element='C', density=2.278e-4, temperature=bulkTemp)
upperExten.addElement(element='Na', density=1.829e-2, temperature=bulkTemp)
upperExten.addElement(element='Si', density=6.959e-4, temperature=bulkTemp)
upperExten.addElement(element='P', density=1.388e-5, temperature=bulkTemp)
upperExten.addElement(element='S', density=7.314e-6, temperature=bulkTemp)
upperExten.addElement(element='Cr', density=1.402e-2, temperature=bulkTemp)
upperExten.addElement(element='Mn', density=5.408e-4, temperature=bulkTemp)
upperExten.addElement(element='Fe', density=4.973e-2, temperature=bulkTemp)
upperExten.addElement(element='Ni', density=5.961e-3, temperature=bulkTemp)

lowerExten = Material(name='lower extension')
lowerExten.addElement(element='C', density=2.190e-4, temperature=bulkTemp)
lowerExten.addElement(element='Na', density=2.145e-2, temperature=bulkTemp)
lowerExten.addElement(element='Si', density=6.690e-4, temperature=bulkTemp)
lowerExten.addElement(element='P', density=1.335e-5, temperature=bulkTemp)
lowerExten.addElement(element='S', density=7.032e-6, temperature=bulkTemp)
lowerExten.addElement(element='Cr', density=1.348e-2, temperature=bulkTemp)
lowerExten.addElement(element='Mn', density=5.199e-4, temperature=bulkTemp)
lowerExten.addElement(element='Fe', density=4.781e-2, temperature=bulkTemp)
lowerExten.addElement(element='Ni', density=5.731e-3, temperature=bulkTemp)

lowerAdap = Material(name='lower adapter')
lowerAdap.addElement(element='C', density=2.483e-4, temperature=bulkTemp)
lowerAdap.addElement(element='Na', density=1.071e-2, temperature=bulkTemp)
lowerAdap.addElement(element='Si', density=7.584e-4, temperature=bulkTemp)
lowerAdap.addElement(element='P', density=1.513e-5, temperature=bulkTemp)
lowerAdap.addElement(element='S', density=7.971e-6, temperature=bulkTemp)
lowerAdap.addElement(element='Cr', density=1.528e-2, temperature=bulkTemp)
lowerAdap.addElement(element='Mn', density=5.894e-4, temperature=bulkTemp)
lowerAdap.addElement(element='Fe', density=5.421e-2, temperature=bulkTemp)
lowerAdap.addElement(element='Ni', density=6.497e-3, temperature=bulkTemp)

wireWrap = Material(name='wire wrap')
wireWrap.addElement(element='C', density=3.209e-4, temperature=bulkTemp)
wireWrap.addElement(element='Si', density=1.715e-3, temperature=bulkTemp)
wireWrap.addElement(element='Cr', density=1.714e-2, temperature=bulkTemp)
wireWrap.addElement(element='Mn', density=3.725e-4, temperature=bulkTemp)
wireWrap.addElement(element='Fe', density=5.643e-2, temperature=bulkTemp)
wireWrap.addElement(element='Ni', density=9.850e-3, temperature=bulkTemp)
wireWrap.addElement(element='Mo', density=1.256e-3, temperature=bulkTemp)

# Wire wrap equivalent
d_Rod = 0.442
d_Wire = 0.1245
d_Eq = d_Rod + 2 * d_Wire
A_wire = 0.25 * pi * (d_Wire**2)
A_sodium = 0.25 * pi * (d_Eq**2 - d_Rod**2)
wireWrapEq = (1 / (A_wire + A_sodium)) * (A_wire * wireWrap + A_sodium * sodium)
wireWrap = wireWrapEq # Replace wire wrap with its equivalent
wireWrap.name = 'Wire Wrap Equivalent'

# HWCR
poisonSlug = Material(name='poison slug')
poisonSlug.addNuclide(nuclide='B10', density=2.169E-2, temperature=bulkTemp)
poisonSlug.addNuclide(nuclide='B11', density=8.730E-2, temperature=bulkTemp)
poisonSlug.addElement(element='C', density=2.725E-2, temperature=bulkTemp)

poisonShieldBlock = Material(name='poison B4C shield block')
poisonShieldBlock.addElement(element='C', density=2.662E-4, temperature=bulkTemp)
poisonShieldBlock.addElement(element='Na', density=3.807E-3, temperature=bulkTemp)
poisonShieldBlock.addElement(element='Si', density=8.133E-4, temperature=bulkTemp)
poisonShieldBlock.addElement(element='P', density=1.622E-5, temperature=bulkTemp)
poisonShieldBlock.addElement(element='S', density=8.548E-6, temperature=bulkTemp)
poisonShieldBlock.addElement(element='Cr', density=1.639E-2, temperature=bulkTemp)
poisonShieldBlock.addElement(element='Mn', density=6.320E-4, temperature=bulkTemp)
poisonShieldBlock.addElement(element='Fe', density=5.812E-2, temperature=bulkTemp)
poisonShieldBlock.addElement(element='Ni', density=6.996E-3, temperature=bulkTemp)

# Safety Ref P123
safetyUpExten = Material(name='upper extension - safety')
safetyUpExten.addElement('C', 2.662E-4, bulkTemp)
safetyUpExten.addElement('Na', 3.807E-3, bulkTemp)
safetyUpExten.addElement('Si', 8.133E-4, bulkTemp)
safetyUpExten.addElement('P', 1.622E-5, bulkTemp)
safetyUpExten.addElement('S', 8.548E-6, bulkTemp)
safetyUpExten.addElement('Cr', 1.639E-2, bulkTemp)
safetyUpExten.addElement('Mn', 6.320E-4, bulkTemp)
safetyUpExten.addElement('Fe', 5.812E-2, bulkTemp)
safetyUpExten.addElement('Ni', 6.966E-3, bulkTemp)

safetyLowAdp = Material(name='lower adapter - safety')
safetyLowAdp.addElement('C', 2.508E-4, bulkTemp)
safetyLowAdp.addElement('Na', 9.748E-3, bulkTemp)
safetyLowAdp.addElement('Si', 7.662E-4, bulkTemp)
safetyLowAdp.addElement('P', 1.529E-5, bulkTemp)
safetyLowAdp.addElement('S', 8.053E-6, bulkTemp)
safetyLowAdp.addElement('Cr', 1.544E-2, bulkTemp)
safetyLowAdp.addElement('Mn', 5.954E-4, bulkTemp)
safetyLowAdp.addElement('Fe', 5.476E-2, bulkTemp)
safetyLowAdp.addElement('Ni', 6.563E-3, bulkTemp)

# reflector
reflectorBlock = Material(name='reflector hex block')
reflectorBlock.addElement('C', 2.667E-4, bulkTemp)
reflectorBlock.addElement('Na', 3.664E-3, bulkTemp)
reflectorBlock.addElement('Si', 8.146E-4, bulkTemp)
reflectorBlock.addElement('P', 1.625E-5, bulkTemp)
reflectorBlock.addElement('S', 8.561E-6, bulkTemp)
reflectorBlock.addElement('Cr', 1.641E-2, bulkTemp)
reflectorBlock.addElement('Mn', 3.403E-3, bulkTemp)
reflectorBlock.addElement('Fe', 5.544E-2, bulkTemp)
reflectorBlock.addElement('Ni', 6.978E-3, bulkTemp)

# print(sodium)
# print(ss304)
# print(ss316)
# print(lowerExten)
# print(upperExten)
# print(lowerAdap)
# print(plenumGas)
# print(wireWrap)


# ######################################################################
#                         Assembly Materials
# 
# The data of materials in this section come from Benchmark CSV Material Data Files, 
# which DO change among assemblies. 
# ######################################################################
benchmarkCsvPath = "C:\\SJTUGraduate\\Research\\Projects\\LoongSARAXVerif\\benchmark\\EBR-II\\EBR2-LMFR-RESR-001\\Benchmark CSV Material Data Files"

class SlugMat:

    def __init__(self, path) -> None:
        """
        SlugMat provides an API to access "Benchmark CSV Material Data Files"
        """
        self.path = path
    
    def get(self, location) -> tuple:
        """
        Get the materials of slugs at given location

        Input
        -----
        location: str or tuple, like "01A01" or (0,0)

        Return
        ------
        A tuple containing three DataFrame:
        ```python
        (DataFrame('ZAIDS', 'Slug1'), DataFrame('ZAIDS', 'Slug2'), DataFrame('ZAIDS', 'Slug3'))
        ```
        """
        # Check input
        if type(location) is tuple:
            location = self.convertLocation(location)
        
        # Open the CSV file at location
        csvPath = self.find(location)
        assemblyMat = pd.read_csv(csvPath)
        slugs = []
        for i in range(1, len(assemblyMat.columns)):
            slugs.append(assemblyMat[['ZAIDS', 'S{:d}'.format(i)]])
            slugs[-1].columns = ('ZAIDS', 'Density')

        return tuple(slugs)

    def find(self, location) -> str:
        """
        Find the CSV Material Data File of assembly at given location
        location: str or tuple, like "01A01" or (0,0)
        """
        # Check input
        if type(location) is tuple:
            location = self.convertLocation(location)
        elif type(location) is not str:
            raise TypeError("Input location is type {}, which should be str or tuple".format(type(location)))
        
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if location in file and 'csv' in file:
                    return os.path.join(root, file)
        
        # Raise error if the input location is NOT found
        raise FileNotFoundError("{} CSV file not found.".format(location))

    def convertLocation(self, location):
        """
        Convert the form of location between (r,k) & "RRSKK"
        """
        # Map from number to section symbol, like 0 -> 'C'
        secMap = [
            (0, 'C'),
            (1, 'D'),
            (2, 'E'),
            (3, 'F'),
            (4, 'A'),
            (5, 'B')
        ]

        # Convert (r,k) to "RRSKK"
        if type(location) is tuple:
            assert len(location) == 2
            r, k = location[0], location[1]
            rr = r + 1
            if rr == 1:
                assert k == 0
                sec = 4 # Section 'A'
                kk = 1
            elif rr > 1:
                sec = k // r
                kk = k % r + 1
            else:
                raise ValueError("Input location {} is invalid.".format(location))
            
            # Map number to symbol, like 0 -> 'C'
            for num, symbol in secMap:
                if num == sec:
                    s = symbol
                    break
            
            return '{:0>2d}{}{:0>2d}'.format(rr, s, kk)
        
        # Convert "RRSKK" to (r,k)
        elif type(location) is str:
            r = int(location[:2]) - 1
            s = location[2]
            kk = int(location[3:])

            # Map symbol to number, like 'C' -> 0
            for num, symbol in secMap:
                if symbol == s:
                    sec = num
                    break
            
            return (r, r * sec + kk - 1)
        
        else:
            raise TypeError("Input location is type {}, which should be tuple or str.".format(type(location)))

    @property
    def allLocations(self) -> tuple:
        """
        Get all locations & their assembly type
        """
        locations = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if 'csv' in file:
                    loc = file.split('.')[0]
                    typ = os.path.split(root)[-1]
                    locations.append((loc, typ))
        
        return locations

slugmat = SlugMat(path=benchmarkCsvPath)


# Test during development
if __name__ == '__main__':
    # result = slugmat.convertLocation(location='10B01')
    # print(result)
    # print(slugmat.find((3,2)))
    # for slug in slugmat.get((0,0)):
    #     print(slug)
    #     print('\n')
    print(slugmat.allLocations)
