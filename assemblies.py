"""
Assemblies File for EBR-II Model

Author: LZK
Date: 2023-1-26
Project: Verification of LoongSARAX Program

File Log:
2023-1-26   File created
2023-1-27   getSecs() completed;
            A simple test passed
2023-1-28   blankAssemb, mapLocType() completed
2023-1-29   buildDrivers() completed
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

from pySARAX import Assembly, Assemblies
from sections import *


# Auxiliary function to get sections from list according to their keys
def getSecs(secs, keys):
    result = []
    for key in keys:
        if type(key) is str:
            result.append(secs[key])
        else:
            result.append(key)
    return result

# ###################################################
#          Assemblies without fuel slug
# ###################################################
assembNoFuel = {}

# Reflector
assembNoFuel['reflector'] =  Assembly(typeName='reflector', location=location)
assembNoFuel['reflector'].sections = getSecs(
    reflectorSecs,
    ['lowAdp', 'lowAssemblyPlug', 'reflectorSlug', 'upAssemblyPlug']
)
assembNoFuel['reflector'].setRefPlane(2, 62.548) # Ref P103 Item:A

# Dummy
assembNoFuel['dummy'] = Assembly(typeName='dummy', location=location)
assembNoFuel['dummy'].sections = getSecs(
    dummySecs,
    ['lowAdp', 'lowAssemblyPlug', 'dummyElement', 'sodiumAboveRod', 'upAssemblyPlug']
)
assembNoFuel['dummy'].setRefPlane(2, 62.5475) # Ref P92 Item:A

# X320C
assembNoFuel['X320C'] = Assembly(typeName='experimental', location=location)
assembNoFuel['X320C'].sections = getSecs(
    dummySecs,
    ['lowAdp', 'lowAssemblyPlug', 'dummyElement', 'sodiumAboveRod', 'upAssemblyPlug']
)
assembNoFuel['X320C'].setRefPlane(2, 62.5475) # Ref P92 Item:A


# ###################################################
#                      Build Function
# ###################################################
def buildAssemb(assemblyType, location, MKType='MKII') -> Assembly:
    """
    Build the assembly at given location

    Input
    -----
    assemblyType: str, the type name of assembly, like 'driver'
    location: str, the location of assembly, like '01A01'
    MKType: str, 'MKII' or 'MKIIA'
    """
    # Pre-processing of experimental assembly
    if assemblyType == 'experimental':
        if location == '04C02': # Identifier: C2776A
            assemblyType = 'C2776A'
        elif location == '04D02':
            assemblyType = 'X320C'
        elif location == '05C01':
            assemblyType = 'XX10'
        elif location == '05D03':
            assemblyType = 'XX09'
        elif location == '05F03':
            assemblyType = 'XY-16'
        elif location == '06B03': # Identifier: X402A
            assemblyType = 'X402A'
        elif location == '06D01': # Identifier: X412
            assemblyType = 'X412'
        else:
            raise ValueError("No experimental assembly at location [{}]".format(location))

    # Find the slug materials at given location
    try:
        if location == 'test':
            slugSecs = (avgFuelSlug.copy(name='Slug{:d}'.format(idx)) for idx in range(1, 4))
        elif assemblyType in ('dummy', 'reflector', 'blank', 'X320C', 'XX10', 'XY-16'):
            pass
        else:
            slugSecs = buildSec(location, assemblyType, slugmat.get(location))
    except FileNotFoundError as err:
        raise RuntimeError("There is NO {} assembly at [{}]".format(assemblyType, location)) from err
    except UnboundLocalError as err:
        print("Error: ({}, {})".format(location, assemblyType))
        raise err

    # Build assembly from sections
    if assemblyType in ('driver', 'HWD', 'C2776A', 'X402A', 'X412'):
        assemblyType = '-'.join((assemblyType, MKType))
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            driverSecs,
            ['lowAdp', 'lowAssemblyPlug', 'lowEx', 'lowCladPlug', *slugSecs, 'sodiumAboveSlug-{}'.format(MKType), 'gasPlenum-{}'.format(MKType), 'upCladPlug-{}'.format(MKType), 'sodiumAboveRod-{}'.format(MKType), 'upEx-{}'.format(MKType), 'upAssemblyPlug-{}'.format(MKType)]
        )
        assembly.setRefPlane(3) # Set lowCladPlug as ref plane
    
    elif assemblyType == 'control':
        assemblyType = '-'.join((assemblyType, MKType))
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            controlSecs,
            ['lowAssemblyPlug', 'lowSodiumGap', 'lowAdp-narrow', 'lowAdp-trans', 'lowAdp-wide', 'medianAssemblyPlug', 'lowCladPlug', *slugSecs, 'sodiumAboveRod', 'gasPlenum', 'upCladPlug', 'medianSodiumGap', 'upEx-low', 'upEx-high']
        )
        assembly.setRefPlane(7, 0.635 - 0.3175) # Ref P96 Item:F

    elif assemblyType == 'safety':
        assemblyType = '-'.join((assemblyType, MKType))
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            safetySecs,
            ['lowAssemblyPlug', 'lowSodiumGap', 'lowAdp-narrow', 'lowAdp-trans', 'lowAdp-wide', 'medianAssemblyPlug', 'lowCladPlug', *slugSecs, 'sodiumAboveRod', 'gasPlenum', 'upCladPlug', 'upSodiumGap', 'upEx', 'upAssemblyPlug']
        )
        assembly.setRefPlane(7, 0.635 - 0.3175)

    elif assemblyType == 'HWCR':
        assemblyType = '-'.join((assemblyType, MKType))
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            hwcrSecs,
            ['lowAssemblyPlug', 'lowSodiumGap', 'lowAdp-wide', 'medianAssemblyPlug', 'lowCladPlug', *slugSecs, 'sodiumAboveRod', 'gasPlenum', 'upCladPlug', 'medianSodiumGap', 'poisonPlug-low', 'poisonSlug', 'poisonSodiumGap', 'poisonShieldBlock', 'poisonGasPlenum', 'upSodiumGap', 'upAssemblyPlug']
        )
        assembly.setRefPlane(5, 8.255 - 0.3175)

    elif assemblyType == 'blanket':
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            blanketSecs,
            ['lowAdp', 'lowAssemblyPlug', *slugSecs, 'sodiumAboveRod', 'gasPlenum', 'sodiumGap', 'upAssemblyPlug']
        )
        assembly.setRefPlane(3, 62.5475 - blanketSecs['lowAssemblyPlug'].height - 46.567) # Ref P108 Item:A

    # elif assemblyType in ('dummy', 'X320C'):
    #     assembly = Assembly(typeName=assemblyType, location=location)
    #     assembly.sections = getSecs(
    #         dummySecs,
    #         ['lowAdp', 'lowAssemblyPlug', 'dummyElement', 'sodiumAboveRod', 'upAssemblyPlug']
    #     )
    #     assembly.setRefPlane(2, 62.5475) # Ref P92 Item:A
    
    elif assemblyType == 'dummy':
        assembly = assembNoFuel['dummy']
    
    elif assemblyType == 'X320C':
        assembly = assembNoFuel['X320C']

    elif assemblyType == 'reflector':
        assembly = assembNoFuel['reflector']
    
    elif assemblyType == 'XX10':
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            xx10Secs,
            ['lowAssemblyPlug', 'lowSodiumGap-narrow', 'lowSodiumGap-trans', 'lowSodiumGap-wide', 'lowEx', 'element', 'upSodiumGap', 'upEx', 'upAssemblyPlug']
        )
        assembly.setRefPlane(5)

    elif assemblyType == 'XX09':
        assembly = Assembly(typeName=assemblyType, location=location)
        assembly.sections = getSecs(
            xx09Secs,
            ['lowAssemblyPlug', 'lowSodiumGap-narrow', 'lowSodiumGap-trans', 'lowSodiumGap-wide', 'lowEx', *slugSecs, 'sodiumAboveRod', 'gasPlenum', 'upSodiumGap', 'upEx', 'upAssemblyPlug']
        )
        assembly.setRefPlane(5)

    elif assemblyType == 'XY-16':
        # assemblyType = '-'.join((assemblyType, MKType))
        assembly = Assembly(typeName=assemblyType, location=location)
        element = dummySecs['dummyElement'].copy(name='dummy element - xy-16')
        element.height = 3 * 11.43
        assembly.sections = getSecs(
            xy16Secs,
            ['lowAssemblyPlug', 'lowSodiumGap', 'lowAdp-narrow', 'lowAdp-trans', 'lowAdp-wide', 'medianAssemblyPlug', 'lowCladPlug', element, 'sodiumAboveRod', 'gasPlenum', 'upCladPlug', 'medianSodiumGap', 'upEx-low', 'upEx-high']
        )
        assembly.setRefPlane(7, 0.635 - 0.3175)
    
    elif assemblyType == 'blank':
        assembly = blankAssemb

    else:
        raise ValueError("Input assembly type {} does NOT exist.".format(assemblyType))

    return assembly


# Build drivers
drivers = {}
# drivers['test-MKII'] = buildAssemb('driver', 'test', 'MKII')
# drivers['test-MKIIA'] = buildAssemb('driver', 'test', 'MKIIA')


# ###################################################
#                      Blank
# 
# Ocupy the blank positions during early test
# Could be DELETED when model completes
# ###################################################
blankAssemb = Assembly(typeName='blank', location='00X00')
blankAssemb.addSection(blankSec, bounds=(-145.188, 143.683))


# ###################################################
#            Map location to assembly type
# 
# An auxiliary function for core.py
# Take in location "01A01", then map it to assembly type "driver-MKII"
# ###################################################
# locTypeTable = pd.read_excel("assembLocations.xlsx")
# locTypeTable['Number'].astype(int)
# locTypeTable['Location'].astype(str)
# print(locTypeTable)

# Convert original type name to standard one
typeNameTable = {
    'MARKII-2AI': 'MKII',
    'MARKII-2A': 'MKIIA',
    'SST': 'dummy',
    'CONTROL': 'control',
    'HWCR': 'HWCR',
    'SafetyRod': 'safety',
    'SSR': 'reflector',
    'Blanket': 'blanket',
    'Instr': 'experimental',
    'XETAGS': 'experimental',
    'Experimental': 'experimental',
    'EXP': 'experimental',
    'EXP-XE': 'experimental'
}

# The numbers of Half-worth drivers
halfWorthDrivers = (1, 2, 4, 6, 9, 11, 13, 17, 66, 75, 79, 90, 120)

# The numbers of assemblies without CSV material file: all reflectors &
assembNoCsv = (24, 38, 52)

# def mapLocType(location):
#     """
#     Map location to assembly type

#     Input
#     -----
#     location: str, like "01A01"

#     Example
#     ------
#     >>> mapLocType('01A01')
#     'driver-MKII'
#     """
