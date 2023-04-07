"""
Sections File for EBR-II Model

Author: LZK
Date: 2023-1-24
Project: Verification of LoongSARAX Program

File Log:
2023-1-24   File created
2023-1-25   pySARAX.Assembly.setRefPlane() added due to modeling need
2023-1-26   Driver completed
2023-1-28   Driver reconstructed using dict
2023-1-30   buildSec() created
2023-1-31   HWD completed
2023-2-1    Control, HWCR, safety & dummy completed
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

import numpy as np
from copy import copy
from pySARAX import Section
from materials import *


# ###################################################
#     Auxiliary function for Half-worth Driver
# ###################################################
def calcShare(location, diameters, SAringNum, SApitch, DRnums, materials):
    """
    SAringNum: ring number of the assembly
    SApitch: pitch of the assembly
    diameters: diameter of rod, gap, clad & wire-wrap in the assembly
    DRnums: ArrayLike, numbers of the dummy rods in every ring
    """
    # diameters拆包
    SAinDiameter = diameters['SA inner']
    SAoutDiameter = diameters['SA outer']
    fuelRodDiameter = diameters['fuel']
    gapDiameter = diameters['gap']
    cladDiameter = diameters['clad']
    wireDiameter = diameters['wire']

    # 计算一根燃料元件内各种材料的面积
    fuelArea = np.pi / 4 * (fuelRodDiameter)**2
    cladArea = np.pi / 4 * (cladDiameter**2 - gapDiameter**2)
    wireArea = np.pi / 4 * (wireDiameter)**2

    # 计算一个哑元件的面积
    DRarea = np.pi / 4 * (cladDiameter)**2

    # 计算各环的等效对边距
    eqRingDiameter = (((SAringNum-1)*SApitch*np.sqrt(3) + cladDiameter) / (2 * SAringNum - 1)) * np.arange(1, 2*SAringNum, 2)

    eqMaterials = {}
    eqSec = Section(name='{} HWD equivalent'.format(location))
    for rid, eqd, DRnum in zip(tuple(range(len(eqRingDiameter))), eqRingDiameter, DRnums):
        rodNum = 6*rid if rid > 0 else 1
        FRnum = rodNum - DRnum
        totalArea = 3.0/np.sqrt(3) * (eqd**2 - eqRingDiameter[rid-1]**2) if rid > 0 else 3.0/np.sqrt(3) * eqd**2
        share = {}
        share['燃料'] = FRnum * fuelArea / totalArea
        share['SS304L'] = (FRnum * cladArea + DRnum * DRarea) / totalArea
        share['燃料棒绕丝'] = (FRnum+DRnum) * wireArea / totalArea
        share['钠'] = 1 - share['燃料'] - share['SS304L'] - share['燃料棒绕丝']

        ringID = str(rid+1)
        eqMaterials[ringID] = {}
        eqMaterials[ringID]['eqDiameter'] = eqd
        eqMat = share['燃料'] * materials['fuel'] + \
                share['SS304L'] * materials['SS304'] + \
                share['钠'] * materials['sodium'] + \
                share['燃料棒绕丝'] * materials['wire']
        
        eqSec.appendRegion(size=eqd, material=eqMat)
        # for elem in elements:
        #     if elem not in eqMaterials[ringID]:
        #         eqMaterials[ringID][elem] = 0.0
        #     for mat in ('燃料', 'SS304L', '燃料棒绕丝', '钠'):
        #         if elem in EDtable[mat]['组分']:
        #             # print(share[mat], EDtable[mat]['组分'][elem])
        #             eqMaterials[ringID][elem] += share[mat] * EDtable[mat]['组分'][elem]
        
    return eqSec



# ###################################################
#                    Build function
# ###################################################
def buildSec(location, secType, slugMats) -> tuple:
    """
    Build the Sections of slugs at given location

    Input
    -----
    location: str, the location of Section, like '01A01'
    secType: str, the type of Section, including ['driver', 'HWD', 'control', 'safety', 'HWCR', 'blanket']
    slugMats: ArrayLike, whose elements are the slug materials, like (DataFrame1(ZAIDS, Density), DataFrame2(ZAIDS, Density), DataFrame3(ZAIDS, Density))

    Example
    -------
    ```python
    >>> slugMats = slugmat.get('01A01')
    (DataFrame at 0x01, DataFrame 0x02, DataFrame 0x03)
    >>> driverSecs['01A01'] = buildSec('01A01', 'driver', slugMats)
    (Section at slug1, Section at slug2, Section at slug3)
    ```
    """
    if secType in ('driver', 'C2776A', 'X412', 'X402A'):
        sections = []
        for idx in range(3):
            secName = ' '.join((location, secType, 'slug{:d}'.format(idx+1)))

            # The material of slugs
            slug = Material(name=secName)
            slug.fromDataFrame(slugMats[idx])

            # Build the section
            sec = Section(name=secName, ring=6, pitch=0.5655, eqMethod='1-D')
            sec.appendRod(0.3302, slug) # Specific material of slug
            sec.appendRod(0.3810, sodium)
            sec.appendRod(0.4420, ss304)
            sec.appendRod(0.4591, wireWrap)
            sec.appendRegion(5.6134, sodium)
            sec.appendRegion(5.8166, ss304)
            sec.appendRegion(5.8929, sodium)
            sec.height = 11.43

            sections.append(sec)
    
    elif secType == 'HWD':
        sections = []
        for idx in range(3):
            secName = ' '.join((location, secType, 'slug{:d}'.format(idx+1)))

            # The material of slugs
            slug = Material(name=secName)
            slug.fromDataFrame(slugMats[idx])

            # Build the section, from inner to outer
            sec = Section(name=secName, ring=ring, pitch=0.5655, eqMethod='1-D')
            cumulativeArea = 0.
            for r in range(ring):
                steelNum = steelNumbers[r]                                   # The number of SS304 rod
                fuelNum = rodNumber(r) - steelNum                            # The number of fuel rod
                
                totalCoef = rodNumber(r) * cellArea                          # Area of current ring
                fuelCoef = fuelNum * fuelArea                                # Area of fuel region
                steelCoef = fuelNum * cladArea + steelNum * steelArea        # Area of SS304 region
                wireCoef = rodNumber(r) * wireArea                           # Area of wire wrap region
                sodiumCoef = totalCoef - (fuelCoef + steelCoef + wireCoef)   # Area of sodium region

                eqPitch = np.sqrt((totalCoef + cumulativeArea) * 4 * np.sqrt(3) / 6)
                # print(r)
                # print(slug.composition)
                # print(fuelCoef)
                # print((fuelCoef * slug).composition)
                eqMat = (1 / totalCoef) * (fuelCoef * slug + steelCoef * ss304 + wireCoef * wireWrap + sodiumCoef * sodium)
                eqMat.name = 'HWD {} Slug{:d} Ring{:d}'.format(location, idx+1, r+1)
                # print(idx, r)
                # print(eqMat.composition.to_string())
                sec.appendRegion(eqPitch, eqMat)

                cumulativeArea += totalCoef
            
            # The outest regions surrounding the equivalent regions
            sec.appendRegion(5.6134, sodium)
            sec.appendRegion(5.8166, ss304)
            sec.appendRegion(5.8929, sodium)
            sec.height = 11.43

            sections.append(sec)

    elif secType in ('control', 'HWCR', 'safety', 'XX09'):
        sections = []
        for idx in range(3):
            secName = ' '.join((location, secType, 'slug{:d}'.format(idx+1)))

            # The material of slugs
            slug = Material(name=secName)
            slug.fromDataFrame(slugMats[idx])

            # Build the section
            sec = Section(name=secName, ring=5, pitch=0.5655, eqMethod='1-D')
            sec.appendRod(0.3302, slug) # Specific material of slug
            sec.appendRod(0.3810, sodium)
            sec.appendRod(0.4420, ss304)
            sec.appendRod(0.4591, wireWrap)
            sec.appendRegion(4.6228, sodium)
            sec.appendRegion(4.8260, ss304)
            sec.appendRegion(5.6134, sodium)
            sec.appendRegion(5.8166, ss304)
            sec.appendRegion(5.8929, sodium)
            sec.height = 11.43

            sections.append(sec)

    elif secType == 'blanket':
        sections = []
        for idx in range(3):
            secName = ' '.join((location, secType, 'slug{:d}'.format(idx+1)))

            # The material of slugs
            slug = Material(name=secName)
            slug.fromDataFrame(slugMats[idx])

            # Build the section
            sec = Section(name=secName, ring=3, pitch=1.2522, eqMethod='1-D')
            sec.appendRod(1.0998, slug) # Specific material of slug
            sec.appendRod(1.0998 + 2 * 0.03048, sodium)
            sec.appendRod(1.2522, ss304)
            sec.appendRegion(5.6134, sodium)
            sec.appendRegion(5.8166, ss304)
            sec.appendRegion(5.8929, sodium)
            sec.height = 46.567

            sections.append(sec)

    elif secType in ('dummy', 'reflector', 'X320C', 'XX10'):
        sections = []

    elif secType == 'XY-16':
        sections = []
        for idx in range(3):
            secName = ' '.join((location, secType, 'slug{:d}'.format(idx+1)))

            # The material of slugs
            slug = Material(name=secName)
            slug.fromDataFrame(slugMats[idx])

            # Build the section
            sec = Section(name=secName, ring=5, pitch=0.5655, eqMethod='1-D')
            sec.appendRod(0.4420, ss304)
            sec.appendRod(0.4591, wireWrap)
            sec.appendRegion(4.6228, sodium)
            sec.appendRegion(4.8260, ss304)
            sec.appendRegion(5.6134, sodium)
            sec.appendRegion(5.8166, ss304)
            sec.appendRegion(5.8929, sodium)
            sec.height = 11.43

            sections.append(sec)
    
    return tuple(sections)


# ###################################################
#                       Fuel Slug
# ###################################################
# Generate the average of ALL fuel material compositions
assembLocPath = "C:\SJTUGraduate\Research\Projects\LoongSARAXVerif\code\model_ver2\\assembLocations.xlsx"
assembLoc = pd.read_excel(assembLocPath)

# # 均匀化燃料芯块(TODO)
# avgFuelSlug = Section(name='average fuel slug', ring=6, pitch=0.5665, eqMethod='1-D')
# avgFuelSlug.appendRod(0.3302, sodium) # Actually it should be avgFuelMat
# avgFuelSlug.appendRod(0.3810, sodium)
# avgFuelSlug.appendRod(0.4420, ss304)
# avgFuelSlug.appendRod(0.4591, wireWrap)
# avgFuelSlug.appendRegion(5.6134, sodium)
# avgFuelSlug.appendRegion(5.8166, ss304)
# avgFuelSlug.appendRegion(5.8929, sodium)
# avgFuelSlug.height = 11.43

# 燃料芯块逐组件详细组分
fuelSlugs = []
for location, assemblyType in slugmat.allLocations:
    mats = slugmat.get(location)
    fuelSlugs.append((location, assemblyType, mats))

blankSec = Section(name='blank')
blankSec.appendRegion(5.8929, sodium)


# ###################################################
#                         Dummy
# ###################################################
dummySecs = {}

# 下适配器
dummySecs['lowAdp'] = Section(name='lower adapter - dummy', ring=1, pitch=0.5665)
dummySecs['lowAdp'].appendRod(4.9070, lowerAdap)
dummySecs['lowAdp'].appendRegion(5.8929, sodium)
dummySecs['lowAdp'].height = 52.07

# 组件端塞
dummySecs['lowAssemblyPlug'] = Section(name='lower assembly plug - dummy')
dummySecs['lowAssemblyPlug'].appendRegion(5.8166, ss304)
dummySecs['lowAssemblyPlug'].appendRegion(5.8929, sodium)
dummySecs['lowAssemblyPlug'].height = 0.1016

dummySecs['upAssemblyPlug'] = dummySecs['lowAssemblyPlug'].copy(name='upper assembly plug - dummy')

# 哑元件区
dummySecs['dummyElement'] = Section(name='dummy element', ring=2, pitch=2.0447)
dummySecs['dummyElement'].appendRod(2.0447, ss304)
dummySecs['dummyElement'].appendRegion(5.6134, sodium)
dummySecs['dummyElement'].appendRegion(5.8166, ss304)
dummySecs['dummyElement'].appendRegion(5.8929, sodium)
dummySecs['dummyElement'].height = 145.2829

# 组件钠腔
dummySecs['sodiumAboveRod'] = Section(name='sodium above rod - dummy')
dummySecs['sodiumAboveRod'].appendRegion(5.6134, sodium)
dummySecs['sodiumAboveRod'].appendRegion(5.8166, ss304)
dummySecs['sodiumAboveRod'].appendRegion(5.8929, sodium)
dummySecs['sodiumAboveRod'].height = 167.199 - dummySecs['dummyElement'].height


# ###################################################
#                         Driver
# 
# 本节描述Driver中各Section的结构，由于Section的实现与轴向坐标紧耦合，
# 对于MKII和MKIIA两种Driver中轴向坐标不同的Section，需使用copy()建立副本，
# 需要建立副本分别描述的Section包括sodium above slug及其上各个Section，
# 即：sodium above slug, gas plenum, upper assembly plug
# ###################################################
driverSecs = {}
# driverSecs['avgFuel'] = avgFuelSlug

# 下适配器
driverSecs['lowAdp'] = Section(name='lower adapter - driver', ring=1, pitch=0.5665)
driverSecs['lowAdp'].appendRod(4.7625, lowerAdap)
driverSecs['lowAdp'].appendRegion(5.8929, sodium)
driverSecs['lowAdp'].height = 51.9125

# 组件端塞
driverSecs['assemblyPlug'] = Section(name='assembly plug')
driverSecs['assemblyPlug'].appendRegion(5.8166, ss304)
driverSecs['assemblyPlug'].appendRegion(5.8929, sodium)

driverSecs['upAssemblyPlug'] = driverSecs['assemblyPlug'].copy(name='upper assembly plug')
driverSecs['upAssemblyPlug'].height = 0.1016
driverSecs['lowAssemblyPlug'] = driverSecs['assemblyPlug'].copy(name='lower assembly plug')
driverSecs['lowAssemblyPlug'].height = 0.1016

driverSecs['upAssemblyPlug-MKII'] = driverSecs['upAssemblyPlug'].copy(name='upper assembly plug - driver MKII')
driverSecs['upAssemblyPlug-MKIIA'] = driverSecs['upAssemblyPlug'].copy(name='upper assembly plug - driver MKIIA')

# 下扩展区 - driver
driverSecs['lowEx'] = Section(name='lower extension - driver')
driverSecs['lowEx'].appendRegion(5.6134, lowerExten)
driverSecs['lowEx'].appendRegion(5.8166, ss304)
driverSecs['lowEx'].appendRegion(5.8929, sodium)
driverSecs['lowEx'].height = 61.3537

# 包壳端盖
driverSecs['cladPlug'] = Section(name='cladding plug', ring=6, pitch=0.5665)
driverSecs['cladPlug'].appendRod(0.4420, ss304)
driverSecs['cladPlug'].appendRod(0.4591, wireWrap)
driverSecs['cladPlug'].appendRegion(5.6134, sodium)
driverSecs['cladPlug'].appendRegion(5.8166, ss304)
driverSecs['cladPlug'].appendRegion(5.8929, sodium)

driverSecs['upCladPlug'] = driverSecs['cladPlug'].copy(name='upper cladding plug')
driverSecs['upCladPlug'].height = 0.6858
driverSecs['lowCladPlug'] = driverSecs['cladPlug'].copy(name='lower cladding plug')
driverSecs['lowCladPlug'].height = 0.3175

driverSecs['upCladPlug-MKII'] = driverSecs['upCladPlug'].copy(name='upper cladding plug - driver MKII')
driverSecs['upCladPlug-MKIIA'] = driverSecs['upCladPlug'].copy(name='upper cladding plug - driver MKIIA')

# 燃料芯块

# 元件钠腔
driverSecs['sodiumAboveSlug'] = Section(name='sodium above slug', ring=6, pitch=0.5665)
driverSecs['sodiumAboveSlug'].appendRod(0.3810, sodium)
driverSecs['sodiumAboveSlug'].appendRod(0.4420, ss304)
driverSecs['sodiumAboveSlug'].appendRod(0.4591, wireWrap)
driverSecs['sodiumAboveSlug'].appendRegion(5.6134, sodium)
driverSecs['sodiumAboveSlug'].appendRegion(5.8166, ss304)
driverSecs['sodiumAboveSlug'].appendRegion(5.8929, sodium)

driverSecs['sodiumAboveSlug-MKII'] = driverSecs['sodiumAboveSlug'].copy(name='sodium above slug - driver MKII') # MK-II <-> MK-IIAI
driverSecs['sodiumAboveSlug-MKII'].height = 3.18
driverSecs['sodiumAboveSlug-MKIIA'] = driverSecs['sodiumAboveSlug'].copy(name='sodium above slug - driver MKIIA')
driverSecs['sodiumAboveSlug-MKIIA'].height = 0.635

# 氦气腔
driverSecs['gasPlenum'] = Section(name='gas plenum', ring=6, pitch=0.5665)
driverSecs['gasPlenum'].appendRod(0.3810, plenumGas)
driverSecs['gasPlenum'].appendRod(0.4420, ss304)
driverSecs['gasPlenum'].appendRod(0.4591, wireWrap)
driverSecs['gasPlenum'].appendRegion(5.6134, sodium)
driverSecs['gasPlenum'].appendRegion(5.8166, ss304)
driverSecs['gasPlenum'].appendRegion(5.8929, sodium)

driverSecs['gasPlenum-MKII'] = driverSecs['gasPlenum'].copy(name='gas plenum - driver MKII')
driverSecs['gasPlenum-MKII'].height = 21.48
driverSecs['gasPlenum-MKIIA'] = driverSecs['gasPlenum'].copy(name='gas plenum - driver MKIIA')
driverSecs['gasPlenum-MKIIA'].height = 24.56

# 组件钠腔
driverSecs['sodiumAboveRod'] = Section(name='sodium above rod')
driverSecs['sodiumAboveRod'].appendRegion(5.6134, sodium)
driverSecs['sodiumAboveRod'].appendRegion(5.8166, ss304)
driverSecs['sodiumAboveRod'].appendRegion(5.8929, sodium)

driverSecs['sodiumAboveRod-MKII'] = driverSecs['sodiumAboveRod'].copy(name='sodium above rod - driver MKII')
driverSecs['sodiumAboveRod-MKII'].height = 8.1317
driverSecs['sodiumAboveRod-MKIIA'] = driverSecs['sodiumAboveRod'].copy(name='sodium above rod - driver MKIIA')
driverSecs['sodiumAboveRod-MKIIA'].height = 5.0517

# 上扩展区 - driver
driverSecs['upEx'] = Section(name='upper extension - driver')
driverSecs['upEx'].appendRegion(5.6134, upperExten)
driverSecs['upEx'].appendRegion(5.8166, ss304)
driverSecs['upEx'].appendRegion(5.8929, sodium)
driverSecs['upEx'].height = 40.5968

driverSecs['upEx-MKII'] = driverSecs['upEx'].copy(name='upper extension - driver MKII')
driverSecs['upEx-MKIIA'] = driverSecs['upEx'].copy(name='upper extension - driver MKIIA')


# ###################################################
#                    Hald-worth Driver
# ###################################################
# HWD采用按环均匀打混的方式建模
steelNumbers = (1, 2, 6, 10, 12, 14)

# Auxiliary: calculate the total & steel rod number in given ring
ring = 6
steelNumbers = (1, 2, 6, 10, 12, 14)
rodNumber = lambda r: 6 * r if r > 0 else 1

# Auxiliary: the areas of structures
fuelArea = np.pi / 4 * 0.3302**2                   # Area of fuel rod
gapArea = np.pi / 4 * 0.3810**2 - fuelArea         # Area of sodium gap
cladArea = np.pi / 4 * 0.4420**2 - gapArea         # Area of SS304 cladding
wireArea = np.pi / 4 * 0.4591**2 - cladArea        # Area of wire wrap
steelArea =  np.pi / 4 * 0.4420**2                 # Area of SS304 dummy rod
cellPitch = 5.6134 / (3 * ring - 1) * np.sqrt(3)   # Pitch of pin cell
cellArea = cellPitch**2 / 4 / np.sqrt(3) * 6       # Area of pin cell


# ###################################################
#                      Control
# ###################################################
controlSecs = {}

# 组件端塞
controlSecs['lowAssemblyPlug'] = driverSecs['lowAssemblyPlug'].copy(name='low assembly plug - control')
controlSecs['upAssemblyPlug'] = driverSecs['upAssemblyPlug-MKII'].copy(name='upper assembly plug - control')

controlSecs['medianAssemblyPlug'] = Section(name='median assembly plug - control')
controlSecs['medianAssemblyPlug'].appendRegion(4.8260, ss304)
controlSecs['medianAssemblyPlug'].appendRegion(5.6134, sodium)
controlSecs['medianAssemblyPlug'].appendRegion(5.8166, ss304)
controlSecs['medianAssemblyPlug'].appendRegion(5.8929, sodium)
controlSecs['medianAssemblyPlug'].height = 0.1016

# 组件钠腔
controlSecs['lowSodiumGap'] = Section(name='lower sodium gap - control')
controlSecs['lowSodiumGap'].appendRegion(5.6134, sodium)
controlSecs['lowSodiumGap'].appendRegion(5.8166, ss304)
controlSecs['lowSodiumGap'].appendRegion(5.8929, sodium)
controlSecs['lowSodiumGap'].height = 37.2534

controlSecs['medianSodiumGap'] = Section(name='median sodium gap - control')
controlSecs['medianSodiumGap'].appendRegion(4.6228, sodium)
controlSecs['medianSodiumGap'].appendRegion(4.8260, ss304)
controlSecs['medianSodiumGap'].appendRegion(5.6134, sodium)
controlSecs['medianSodiumGap'].appendRegion(5.8166, ss304)
controlSecs['medianSodiumGap'].appendRegion(5.8929, sodium)
controlSecs['medianSodiumGap'].height = 15.5781

controlSecs['upSodiumGap'] = Section(name='upper sodium gap - control')
controlSecs['upSodiumGap'].appendRegion(4.6228, sodium)
controlSecs['upSodiumGap'].appendRegion(4.8260, ss304)
controlSecs['upSodiumGap'].appendRegion(5.8929, sodium)
controlSecs['upSodiumGap'].height = 36.0750

# 下适配器
controlSecs['lowAdp-narrow'] = Section(name='lower adapter narrow - control', ring=1, pitch=0.5665)
controlSecs['lowAdp-narrow'].appendRod(4.2910, lowerAdap)
controlSecs['lowAdp-narrow'].appendRegion(5.4282, sodium)
controlSecs['lowAdp-narrow'].appendRegion(5.6314, ss304)
controlSecs['lowAdp-narrow'].appendRegion(5.8929, sodium)
controlSecs['lowAdp-narrow'].height = 19.6854

controlSecs['lowAdp-trans'] = Section(name='lower adapter trans - control', ring=1, pitch=0.5665)
controlSecs['lowAdp-trans'].appendRod(4.2910, lowerAdap)
controlSecs['lowAdp-trans'].appendRegion(5.4282, sodium)
controlSecs['lowAdp-trans'].appendRegion(5.8166, ss304)
controlSecs['lowAdp-trans'].appendRegion(5.8929, sodium)
controlSecs['lowAdp-trans'].height = 0.1016

controlSecs['lowAdp-wide'] = Section(name='lower adapter narrow - control', ring=1, pitch=0.5665)
controlSecs['lowAdp-wide'].appendRod(4.2910, lowerAdap)
controlSecs['lowAdp-wide'].appendRegion(5.6134, sodium)
controlSecs['lowAdp-wide'].appendRegion(5.8166, ss304)
controlSecs['lowAdp-wide'].appendRegion(5.8929, sodium)
controlSecs['lowAdp-wide'].height = 61.4360

# 包壳端盖
controlSecs['lowCladPlug'] = Section(name='lower cladding plug - control', ring=6, pitch=0.5665)
controlSecs['lowCladPlug'].appendRod(0.4420, ss304)
controlSecs['lowCladPlug'].appendRod(0.4591, wireWrap)
controlSecs['lowCladPlug'].appendRegion(4.6228, sodium)
controlSecs['lowCladPlug'].appendRegion(4.8260, ss304)
controlSecs['lowCladPlug'].appendRegion(5.6134, sodium)
controlSecs['lowCladPlug'].appendRegion(5.8166, ss304)
controlSecs['lowCladPlug'].appendRegion(5.8929, sodium)
controlSecs['lowCladPlug'].height = 0.3175

controlSecs['upCladPlug'] = controlSecs['lowCladPlug'].copy(name='upper cladding plug - control')
controlSecs['upCladPlug'].height = 0.6858

# 燃料芯块

# 元件钠腔
controlSecs['sodiumAboveRod'] = Section(name='sodium above rod - control', ring=5, pitch=0.5665)
controlSecs['sodiumAboveRod'].appendRod(0.3810, sodium)
controlSecs['sodiumAboveRod'].appendRod(0.4420, ss304)
controlSecs['sodiumAboveRod'].appendRod(0.4591, wireWrap)
controlSecs['sodiumAboveRod'].appendRegion(4.6228, sodium)
controlSecs['sodiumAboveRod'].appendRegion(4.8260, ss304)
controlSecs['sodiumAboveRod'].appendRegion(5.4282, sodium)
controlSecs['sodiumAboveRod'].appendRegion(5.8166, ss304)
controlSecs['sodiumAboveRod'].appendRegion(5.8929, sodium)
controlSecs['sodiumAboveRod'].height = 0.635
# controlSecs['sodiumAboveRod'].height = 3.180

# 氦气腔
controlSecs['gasPlenum'] = Section(name='gas plenum - control', ring=5, pitch=0.5665)
controlSecs['gasPlenum'].appendRod(0.3810, plenumGas)
controlSecs['gasPlenum'].appendRod(0.4420, ss304)
controlSecs['gasPlenum'].appendRod(0.4591, wireWrap)
controlSecs['gasPlenum'].appendRegion(4.6228, sodium)
controlSecs['gasPlenum'].appendRegion(4.8260, ss304)
controlSecs['gasPlenum'].appendRegion(5.4282, sodium)
controlSecs['gasPlenum'].appendRegion(5.8166, ss304)
controlSecs['gasPlenum'].appendRegion(5.8929, sodium)
controlSecs['gasPlenum'].height = 24.56
# controlSecs['gasPlenum'].height = 21.48

# 上部扩展区
controlSecs['upEx-low'] = Section(name='lower part of upper extension - control')
controlSecs['upEx-low'].appendRegion(4.6228, upperExten)
controlSecs['upEx-low'].appendRegion(4.8260, ss304)
controlSecs['upEx-low'].appendRegion(5.6134, sodium)
controlSecs['upEx-low'].appendRegion(5.8166, ss304)
controlSecs['upEx-low'].appendRegion(5.8929, sodium)
controlSecs['upEx-low'].height = 22.955

controlSecs['upEx-high'] = Section(name='higher part of upper extension - control')
controlSecs['upEx-high'].appendRegion(4.6228, upperExten)
controlSecs['upEx-high'].appendRegion(4.8260, ss304)
controlSecs['upEx-high'].appendRegion(5.8929, sodium)
controlSecs['upEx-high'].height = 7.5250


# ###################################################
#                        HWCR
# ###################################################
hwcrSecs = {}

# 组件端塞
hwcrSecs['lowAssemblyPlug'] = controlSecs['lowAssemblyPlug'].copy(name='lower assembly plug - HWCR')
hwcrSecs['medianAssemblyPlug'] = controlSecs['medianAssemblyPlug'].copy(name='median assembly plug - HWCR')
hwcrSecs['upAssemblyPlug'] = controlSecs['upAssemblyPlug'].copy(name='upper assembly plug - HWCR')

# 组件钠腔
hwcrSecs['lowSodiumGap'] = controlSecs['lowSodiumGap'].copy(name='lower sodium gap - HWCR')
hwcrSecs['lowSodiumGap'].height = 63.7290

hwcrSecs['medianSodiumGap'] = controlSecs['medianSodiumGap'].copy(name='median sodium gap - HWCR')
hwcrSecs['medianSodiumGap'].height = 3.18

hwcrSecs['upSodiumGap'] = controlSecs['upSodiumGap'].copy(name='upper sodium gap - HWCR')
hwcrSecs['upSodiumGap'].height = 6.0340

# 下适配器 (TODO)
# hwcrSecs['lowAdp-narrow'] = controlSecs['lowAdp-narrow'].copy(name='lower adapter narrow - HWCR')
# hwcrSecs['lowAdp-narrow'].height = 0.

# hwcrSecs['lowAdp-trans'] = controlSecs['lowAdp-trans'].copy(name='lower adapter trans - HWCR')
# hwcrSecs['lowAdp-trans'].height = 0.

hwcrSecs['lowAdp-wide'] = controlSecs['lowAdp-wide'].copy(name='lower adapter wide - HWCR')
hwcrSecs['lowAdp-wide'].height = 52.230

# 元件端盖
hwcrSecs['lowCladPlug'] = controlSecs['lowCladPlug'].copy(name='lower cladding plug - HWCR')
hwcrSecs['upCladPlug'] = controlSecs['upCladPlug'].copy(name='upper cladding plug - HWCR')

# 燃料芯块

# 元件钠腔
hwcrSecs['sodiumAboveRod'] = controlSecs['sodiumAboveRod'].copy(name='sodium above rod - HWCR')

# 氦气腔
hwcrSecs['gasPlenum'] = controlSecs['gasPlenum'].copy(name='gas plenum - HWCR')

# 毒物棒端盖
hwcrSecs['poisonPlug-low'] = Section(name='poison rod lower plug', ring=2, pitch=1.664)
hwcrSecs['poisonPlug-low'].appendRod(1.5875, ss316)
hwcrSecs['poisonPlug-low'].appendRod(1.5923, wireWrap)
hwcrSecs['poisonPlug-low'].appendRegion(4.6228, sodium)
hwcrSecs['poisonPlug-low'].appendRegion(4.8260, ss304)
hwcrSecs['poisonPlug-low'].appendRegion(5.6134, sodium)
hwcrSecs['poisonPlug-low'].appendRegion(5.8166, ss304)
hwcrSecs['poisonPlug-low'].appendRegion(5.8929, sodium)
hwcrSecs['poisonPlug-low'].height = 1.27

# hwcrSecs['poisonPlug-up'] = hwcrSecs['poisonPlug-low'].copy(name='poison rod upper plug', ring=2, pitch=1.664)
# hwcrSecs['poisonPlug-up'].height = 0.6858

# 毒物芯块
hwcrSecs['poisonSlug'] = Section(name='poison slug', ring=2, pitch=1.664, eqMethod='supercell')
hwcrSecs['poisonSlug'].appendRod(1.3754, poisonSlug)
hwcrSecs['poisonSlug'].appendRod(1.4097, sodium)
hwcrSecs['poisonSlug'].appendRod(1.5875, ss316)
hwcrSecs['poisonSlug'].appendRod(1.5923, wireWrap)
hwcrSecs['poisonSlug'].appendRegion(4.6228, sodium)
hwcrSecs['poisonSlug'].appendRegion(4.8260, ss304)
hwcrSecs['poisonSlug'].appendRegion(5.6134, sodium)
hwcrSecs['poisonSlug'].appendRegion(5.8166, ss304)
hwcrSecs['poisonSlug'].appendRegion(5.8929, sodium)
hwcrSecs['poisonSlug'].height = 35.56
# hwcrSecs['poisonSlug'].scSection = buildSec('04A02', 'driver', slugmat.get(location=('04A02')))[0]
hwcrSecs['poisonSlug'].scSection = driverSecs['upEx-MKII'] # Surrounding the poison in HWCR are upper extension and gas plenum
# hwcrSecs['poisonSlug'].scSection = None # NEED to specify the surrounding assemblies of supercell

# # 7个HWCR周围组件的编号
# hwcrSurroundings = {
#     '05C03': (21, 22, 39, 41, 64, 65),
#     '05E01': (26, 45, 47, 71, 72, 73),
#     '05E03': (27, 28, 47, 49, 74, 75),
#     '05F01': (29, 49, 51, 76, 77, 78),
#     '05A01': (32, 53, 55, 81, 82, 83),
#     '05B01': (35, 57, 59, 86, 87, 88),
#     '05B03': (36, 37, 59, 61, 89, 90)
# }

# # 遍历生成所有HWCR
# for hwcrLoc in hwcrSurroundings.keys():
#     slugName = '-'.join(('poisonSlug'), hwcrLoc)
#     hwcrSecs[slugName] = hwcrSecs['poisonSlug'].copy(name=slugName)

#     surroundMats = []
#     for surroundNum in hwcrSurroundings[hwcrLoc]:
#         surroundLoc = assembLoc[assembLoc['Number'] == surroundNum]['Location']
#         surroundMats.append(slugmat.get(surroundLoc))
#     # hwcrSecs[slugName].scSection = 

# 毒物棒钠腔
hwcrSecs['poisonSodiumGap'] = Section(name='poison rod sodium gap', ring=2, pitch=1.664)
hwcrSecs['poisonSodiumGap'].appendRod(1.4097, sodium)
hwcrSecs['poisonSodiumGap'].appendRod(1.5875, ss316)
hwcrSecs['poisonSodiumGap'].appendRod(1.5923, wireWrap)
hwcrSecs['poisonSodiumGap'].appendRegion(4.6228, sodium)
hwcrSecs['poisonSodiumGap'].appendRegion(4.8260, ss304)
hwcrSecs['poisonSodiumGap'].appendRegion(5.6134, sodium)
hwcrSecs['poisonSodiumGap'].appendRegion(5.8166, ss304)
hwcrSecs['poisonSodiumGap'].appendRegion(5.8929, sodium)
hwcrSecs['poisonSodiumGap'].height = 3.4930

# 毒物棒屏蔽块
hwcrSecs['poisonShieldBlock'] = Section(name='poison rod shield block', ring=2, pitch=1.664)
hwcrSecs['poisonShieldBlock'].appendRod(1.4097, poisonShieldBlock)
hwcrSecs['poisonShieldBlock'].appendRod(1.5875, ss316)
hwcrSecs['poisonShieldBlock'].appendRod(1.5923, wireWrap)
hwcrSecs['poisonShieldBlock'].appendRegion(4.6228, sodium)
hwcrSecs['poisonShieldBlock'].appendRegion(4.8260, ss304)
hwcrSecs['poisonShieldBlock'].appendRegion(5.6134, sodium)
hwcrSecs['poisonShieldBlock'].appendRegion(5.8166, ss304)
hwcrSecs['poisonShieldBlock'].appendRegion(5.8929, sodium)
hwcrSecs['poisonShieldBlock'].height = 20.32

# 毒物棒氦气腔
hwcrSecs['poisonGasPlenum'] = Section(name='poison rod gas plenum', ring=2, pitch=1.664)
hwcrSecs['poisonGasPlenum'].appendRod(1.4097, plenumGas)
hwcrSecs['poisonGasPlenum'].appendRod(1.5875, ss316)
hwcrSecs['poisonGasPlenum'].appendRod(1.5923, wireWrap)
hwcrSecs['poisonGasPlenum'].appendRegion(4.6228, sodium)
hwcrSecs['poisonGasPlenum'].appendRegion(4.8260, ss304)
hwcrSecs['poisonGasPlenum'].appendRegion(5.6134, sodium)
hwcrSecs['poisonGasPlenum'].appendRegion(5.8166, ss304)
hwcrSecs['poisonGasPlenum'].appendRegion(5.8929, sodium)
hwcrSecs['poisonGasPlenum'].height = 31.0340


# ###################################################
#                       Safety
# ###################################################
safetySecs = {}

# 组件端塞
safetySecs['lowAssemblyPlug'] = controlSecs['lowAssemblyPlug'].copy(name='lower assembly plug - safety')
safetySecs['medianAssemblyPlug'] = controlSecs['medianAssemblyPlug'].copy(name='median assembly plug - safety')
safetySecs['upAssemblyPlug'] = controlSecs['upAssemblyPlug'].copy(name='upper assembly plug - safety')

# 组件钠腔
safetySecs['lowSodiumGap'] = controlSecs['lowSodiumGap'].copy(name='lower sodium gap - safety')
safetySecs['lowSodiumGap'].height = 61.7520

safetySecs['upSodiumGap'] = controlSecs['upSodiumGap'].copy(name='upper sodium gap - safety')
safetySecs['upSodiumGap'].height = 5.1679

# 下适配器
safetySecs['lowAdp-narrow'] = Section(name='lower adapter narrow - safety', ring=1, pitch=0.5665)
safetySecs['lowAdp-narrow'].appendRod(4.2910, safetyLowAdp)
safetySecs['lowAdp-narrow'].appendRegion(5.4282, sodium)
safetySecs['lowAdp-narrow'].appendRegion(5.6314, ss304)
safetySecs['lowAdp-narrow'].appendRegion(5.8929, sodium)
safetySecs['lowAdp-narrow'].height = 20.8764

safetySecs['lowAdp-trans'] = Section(name='lower adapter trans - safety', ring=1, pitch=0.5665)
safetySecs['lowAdp-trans'].appendRod(4.2910, safetyLowAdp)
safetySecs['lowAdp-trans'].appendRegion(5.4282, sodium)
safetySecs['lowAdp-trans'].appendRegion(5.8166, ss304)
safetySecs['lowAdp-trans'].appendRegion(5.8929, sodium)
safetySecs['lowAdp-trans'].height = 0.1016

safetySecs['lowAdp-wide'] = Section(name='lower adapter narrow - safety', ring=1, pitch=0.5665)
safetySecs['lowAdp-wide'].appendRod(4.2910, safetyLowAdp)
safetySecs['lowAdp-wide'].appendRegion(5.6134, sodium)
safetySecs['lowAdp-wide'].appendRegion(5.8166, ss304)
safetySecs['lowAdp-wide'].appendRegion(5.8929, sodium)
safetySecs['lowAdp-wide'].height = 61.6570

# 元件端盖
safetySecs['lowCladPlug'] = controlSecs['lowCladPlug'].copy(name='lower cladding plug - safety')

safetySecs['upCladPlug'] = Section(name='upper cladding plug - safety', ring=5, pitch=0.5665)
safetySecs['upCladPlug'].appendRod(0.4420, ss304)
safetySecs['upCladPlug'].appendRod(0.4591, wireWrap)
safetySecs['upCladPlug'].appendRegion(4.6228, sodium)
safetySecs['upCladPlug'].appendRegion(4.8260, ss304)
safetySecs['upCladPlug'].appendRegion(5.8929, sodium)
safetySecs['upCladPlug'].height = 0.6858

# 燃料芯块

# 元件钠腔
safetySecs['sodiumAboveRod'] = controlSecs['sodiumAboveRod'].copy(name='sodium above rod - safety')

# 氦气腔
safetySecs['gasPlenum'] = Section(name='gas plenum - safety', ring=5, pitch=0.5665)
safetySecs['gasPlenum'].appendRod(0.3810, plenumGas)
safetySecs['gasPlenum'].appendRod(0.4420, ss304)
safetySecs['gasPlenum'].appendRod(0.4591, wireWrap)
safetySecs['gasPlenum'].appendRegion(4.6228, sodium)
safetySecs['gasPlenum'].appendRegion(4.8260, ss304)
safetySecs['gasPlenum'].appendRegion(5.8929, sodium)
safetySecs['gasPlenum'].height = 24.56

# 上扩展区
safetySecs['upEx'] = Section(name='upper extension - safety')
safetySecs['upEx'].appendRegion(4.6228, safetyUpExten)
safetySecs['upEx'].appendRegion(4.8260, ss304)
safetySecs['upEx'].appendRegion(5.8929, sodium)
safetySecs['upEx'].height = 37.305


# ###################################################
#                       Blanket
# ###################################################
blanketSecs = {}

# 下适配器
blanketSecs['lowAdp'] = Section(name='lower adapter - blanket', ring=1, pitch=0.5665)
blanketSecs['lowAdp'].appendRod(3.8280, lowerAdap)
blanketSecs['lowAdp'].appendRegion(5.8929, sodium)
blanketSecs['lowAdp'].height = 52.07

# 组件端塞
blanketSecs['lowAssemblyPlug'] = Section(name='lower assembly plug - blanket')
blanketSecs['lowAssemblyPlug'].appendRegion(5.8166, ss304)
blanketSecs['lowAssemblyPlug'].appendRegion(5.8929, sodium)
blanketSecs['lowAssemblyPlug'].height = 0.1016

blanketSecs['upAssemblyPlug'] = blanketSecs['lowAssemblyPlug'].copy(name='upper assembly plug - blanket')

# 包壳端盖
blanketSecs['lowCladPlug'] = Section(name='lower cladding plug - blanket', ring=3, pitch=1.2522)
blanketSecs['lowCladPlug'].appendRod(1.2522, ss304)
blanketSecs['lowCladPlug'].appendRegion(5.6134, sodium)
blanketSecs['lowCladPlug'].appendRegion(5.8166, ss304)
blanketSecs['lowCladPlug'].appendRegion(5.8929, sodium)
blanketSecs['lowCladPlug'].height = 0.04572

blanketSecs['upCladPlug'] = blanketSecs['lowCladPlug'].copy(name='upper cladding plug - blanket')

# 增殖芯块

# 元件钠腔
blanketSecs['sodiumAboveRod'] = Section(name='sodium above rod - blanket', ring=3, pitch=1.2522)
blanketSecs['sodiumAboveRod'].appendRod(2*0.03048 + 1.0998, sodium)
blanketSecs['sodiumAboveRod'].appendRod(1.2522, ss304)
blanketSecs['sodiumAboveRod'].appendRegion(5.6134, sodium)
blanketSecs['sodiumAboveRod'].appendRegion(5.8166, ss304)
blanketSecs['sodiumAboveRod'].appendRegion(5.8929, sodium)
blanketSecs['sodiumAboveRod'].height = 3.048

# 氦气腔
blanketSecs['gasPlenum'] = Section(name='gas plenum - blanket', ring=3, pitch=1.2522)
blanketSecs['gasPlenum'].appendRod(1.0998, plenumGas)
blanketSecs['gasPlenum'].appendRod(2*0.03048 + 1.0998, sodium)
blanketSecs['gasPlenum'].appendRod(1.2522, ss304)
blanketSecs['gasPlenum'].appendRegion(5.6134, sodium)
blanketSecs['gasPlenum'].appendRegion(5.8166, ss304)
blanketSecs['gasPlenum'].appendRegion(5.8929, sodium)
blanketSecs['gasPlenum'].height = 12.76

# 组件钠腔
blanketSecs['sodiumGap'] = Section(name='sodium gap - blanket')
blanketSecs['sodiumGap'].appendRegion(5.6134, sodium)
blanketSecs['sodiumGap'].appendRegion(5.8166, ss304)
blanketSecs['sodiumGap'].appendRegion(5.8929, sodium)
blanketSecs['sodiumGap'].height = 158.234 - 2 * blanketSecs['upCladPlug'].height - 3 * 46.567 - blanketSecs['sodiumAboveRod'].height - blanketSecs['gasPlenum'].height


# ###################################################
#                       Reflector
# ###################################################
reflectorSecs = {}

# 下适配器
reflectorSecs['lowAdp'] = Section(name='lower adapter - reflector', ring=1, pitch=0.5665)
reflectorSecs['lowAdp'].appendRod(4.2910, lowerAdap)
reflectorSecs['lowAdp'].appendRegion(5.8929, sodium)
reflectorSecs['lowAdp'].height = 52.07

# 组件端塞
reflectorSecs['lowAssemblyPlug'] = Section(name='lower assembly plug - reflector')
reflectorSecs['lowAssemblyPlug'].appendRegion(5.8166, ss304)
reflectorSecs['lowAssemblyPlug'].appendRegion(5.8929, sodium)
reflectorSecs['lowAssemblyPlug'].height = 0.1016

reflectorSecs['upAssemblyPlug'] = reflectorSecs['lowAssemblyPlug'].copy(name='upper assembly plug - reflector')

# 反射芯块
reflectorSecs['reflectorSlug'] = Section(name='reflector slug')
reflectorSecs['reflectorSlug'].appendRegion(5.6134, reflectorBlock)
reflectorSecs['reflectorSlug'].appendRegion(5.8166, ss304)
reflectorSecs['reflectorSlug'].appendRegion(5.8929, sodium)
reflectorSecs['reflectorSlug'].height = 163.909


# ###################################################
#                Experimental - XX10
# ###################################################
xx10Secs = {}

# 组件端塞
xx10Secs['lowAssemblyPlug'] = Section(name='lower assembly plug - xx10')
xx10Secs['lowAssemblyPlug'].appendRegion(4.8260, ss304)
xx10Secs['lowAssemblyPlug'].appendRegion(5.8929, sodium)
xx10Secs['lowAssemblyPlug'].height = 0.1016

xx10Secs['upAssemblyPlug'] = xx10Secs['lowAssemblyPlug'].copy(name='upper assembly plug - xx10')

# 组件钠腔
xx10Secs['lowSodiumGap-narrow'] = Section(name='lower sodium gap narrow - xx10')
xx10Secs['lowSodiumGap-narrow'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx10Secs['lowSodiumGap-narrow'].appendRegion(4.8260, ss304)
xx10Secs['lowSodiumGap-narrow'].appendRegion(5.8929, sodium)
xx10Secs['lowSodiumGap-narrow'].height = 108.618 - 2 * 0.1016 - 52.23

xx10Secs['lowSodiumGap-trans'] = Section(name='lower sodium gap trans - xx10')
xx10Secs['lowSodiumGap-trans'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx10Secs['lowSodiumGap-trans'].appendRegion(5.8166, ss304)
xx10Secs['lowSodiumGap-trans'].appendRegion(5.8929, sodium)
xx10Secs['lowSodiumGap-trans'].height = 0.1016

xx10Secs['lowSodiumGap-wide'] = Section(name='lower sodium gap wide - xx10')
xx10Secs['lowSodiumGap-wide'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx10Secs['lowSodiumGap-wide'].appendRegion(5.8166, ss304)
xx10Secs['lowSodiumGap-wide'].appendRegion(5.8929, sodium)
xx10Secs['lowSodiumGap-wide'].height = 52.23 - 40.597 # Estimated

xx10Secs['upSodiumGap'] = Section(name='upper sodium gap - xx10')
xx10Secs['upSodiumGap'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx10Secs['upSodiumGap'].appendRegion(4.8260, ss304)
xx10Secs['upSodiumGap'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx10Secs['upSodiumGap'].appendRegion(5.8166, ss304)
xx10Secs['upSodiumGap'].appendRegion(5.8929, sodium)
xx10Secs['upSodiumGap'].height = 68.428 - 61.2

# 下扩展区
xx10Secs['lowEx'] = Section(name='lower extension - xx10', ring=1, pitch=0.5665)
xx10Secs['lowEx'].appendRegion(4.8260 - 2 * 0.1016, lowerExten)
xx10Secs['lowEx'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx10Secs['lowEx'].appendRegion(5.8166, ss304)
xx10Secs['lowEx'].appendRegion(5.8929, sodium)
xx10Secs['lowEx'].height = 40.597 # Estimated

# 哑元件区
xx10Secs['element'] = Section(name='dummy element - xx10', ring=3, pitch=1.0055)
xx10Secs['element'].appendRod(0.8810, ss316)
xx10Secs['element'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx10Secs['element'].appendRegion(4.8260, ss304)
xx10Secs['element'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx10Secs['element'].appendRegion(5.8166, ss304)
xx10Secs['element'].appendRegion(5.8929, sodium)
xx10Secs['element'].height = 61.2

# 上扩展区
xx10Secs['upEx'] = Section(name='upper extension - xx10')
xx10Secs['upEx'].appendRegion(4.8260 - 2 * 0.1016, upperExten)
xx10Secs['upEx'].appendRegion(4.8260, ss304)
xx10Secs['upEx'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx10Secs['upEx'].appendRegion(5.8166, ss304)
xx10Secs['upEx'].appendRegion(5.8929, sodium)
xx10Secs['upEx'].height = 40.597 - 0.1016


# ###################################################
#                 Experimental - XX09
# ###################################################
xx09Secs = {}

# 组件端塞
xx09Secs['lowAssemblyPlug'] = Section(name='lower assembly plug - xx09')
xx09Secs['lowAssemblyPlug'].appendRegion(4.8260, ss304)
xx09Secs['lowAssemblyPlug'].appendRegion(5.8929, sodium)
xx09Secs['lowAssemblyPlug'].height = 0.1016

xx09Secs['upAssemblyPlug'] = xx09Secs['lowAssemblyPlug'].copy(name='upper assembly plug - xx09')

# 组件钠腔
xx09Secs['lowSodiumGap-narrow'] = Section(name='lower sodium gap narrow - xx09')
xx09Secs['lowSodiumGap-narrow'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx09Secs['lowSodiumGap-narrow'].appendRegion(4.8260, ss304)
xx09Secs['lowSodiumGap-narrow'].appendRegion(5.8929, sodium)
xx09Secs['lowSodiumGap-narrow'].height = 108.618 - 2 * 0.1016 - 52.23

xx09Secs['lowSodiumGap-trans'] = Section(name='lower sodium gap trans - xx09')
xx09Secs['lowSodiumGap-trans'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx09Secs['lowSodiumGap-trans'].appendRegion(5.8166, ss304)
xx09Secs['lowSodiumGap-trans'].appendRegion(5.8929, sodium)
xx09Secs['lowSodiumGap-trans'].height = 0.1016

xx09Secs['lowSodiumGap-wide'] = Section(name='lower sodium gap wide - xx09')
xx09Secs['lowSodiumGap-wide'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx09Secs['lowSodiumGap-wide'].appendRegion(5.8166, ss304)
xx09Secs['lowSodiumGap-wide'].appendRegion(5.8929, sodium)
xx09Secs['lowSodiumGap-wide'].height = 52.23 - 40.597 # Estimated

xx09Secs['upSodiumGap'] = Section(name='upper sodium gap - xx09')
xx09Secs['upSodiumGap'].appendRegion(4.8260 - 2 * 0.1016, sodium)
xx09Secs['upSodiumGap'].appendRegion(4.8260, ss304)
xx09Secs['upSodiumGap'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx09Secs['upSodiumGap'].appendRegion(5.8166, ss304)
xx09Secs['upSodiumGap'].appendRegion(5.8929, sodium)
xx09Secs['upSodiumGap'].height = 68.428 - 61.2

# 下扩展区
xx09Secs['lowEx'] = Section(name='lower extension - xx09', ring=1, pitch=0.5665)
xx09Secs['lowEx'].appendRegion(4.8260 - 2 * 0.1016, lowerExten)
xx09Secs['lowEx'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx09Secs['lowEx'].appendRegion(5.8166, ss304)
xx09Secs['lowEx'].appendRegion(5.8929, sodium)
xx09Secs['lowEx'].height = 40.597 # Estimated

# 包壳端盖
xx09Secs['lowCladPlug'] = Section(name='lower cladding plug', ring=5, pitch=0.5665)
xx09Secs['lowCladPlug'].appendRod(0.4420, ss304)
xx09Secs['lowCladPlug'].appendRod(0.4591, wireWrap)
xx09Secs['lowCladPlug'].appendRegion(4.6228, sodium)
xx09Secs['lowCladPlug'].appendRegion(4.8260, ss304)
xx09Secs['lowCladPlug'].appendRegion(5.4282, sodium)
xx09Secs['lowCladPlug'].appendRegion(5.8166, ss304)
xx09Secs['lowCladPlug'].appendRegion(5.8929, sodium)
xx09Secs['lowCladPlug'].height = 0.1016

# 燃料芯块

# 元件钠腔
xx09Secs['sodiumAboveRod'] = Section(name='sodium above rod - xx09', ring=6, pitch=0.5665)
xx09Secs['sodiumAboveRod'].appendRod(0.3810, sodium)
xx09Secs['sodiumAboveRod'].appendRod(0.4420, ss304)
xx09Secs['sodiumAboveRod'].appendRod(0.4591, wireWrap)
xx09Secs['sodiumAboveRod'].appendRegion(4.6228, sodium)
xx09Secs['sodiumAboveRod'].appendRegion(4.8260, ss304)
xx09Secs['sodiumAboveRod'].appendRegion(5.4282, sodium)
xx09Secs['sodiumAboveRod'].appendRegion(5.8166, ss304)
xx09Secs['sodiumAboveRod'].appendRegion(5.8929, sodium)
xx09Secs['sodiumAboveRod'].height = 0.635

# 氦气腔
xx09Secs['gasPlenum'] = Section(name='gas plenum - xx09', ring=6, pitch=0.5665)
xx09Secs['gasPlenum'].appendRod(0.3810, plenumGas)
xx09Secs['gasPlenum'].appendRod(0.4420, ss304)
xx09Secs['gasPlenum'].appendRod(0.4591, wireWrap)
xx09Secs['gasPlenum'].appendRegion(4.6228, sodium)
xx09Secs['gasPlenum'].appendRegion(4.8260, ss304)
xx09Secs['gasPlenum'].appendRegion(5.4282, sodium)
xx09Secs['gasPlenum'].appendRegion(5.8166, ss304)
xx09Secs['gasPlenum'].appendRegion(5.8929, sodium)
xx09Secs['gasPlenum'].height = 24.56

# 上扩展区
xx09Secs['upEx'] = Section(name='upper extension - xx09')
xx09Secs['upEx'].appendRegion(4.8260 - 2 * 0.1016, upperExten)
xx09Secs['upEx'].appendRegion(4.8260, ss304)
xx09Secs['upEx'].appendRegion(5.8166 - 2 * 0.1016, sodium)
xx09Secs['upEx'].appendRegion(5.8166, ss304)
xx09Secs['upEx'].appendRegion(5.8929, sodium)
xx09Secs['upEx'].height = 40.597 - 0.1016


# ###################################################
#                       XY-16
# ###################################################
xy16Secs = {}

# 组件端塞
xy16Secs['lowAssemblyPlug'] = controlSecs['lowAssemblyPlug'].copy(name='low assembly plug - xy-16')
xy16Secs['upAssemblyPlug'] = controlSecs['upAssemblyPlug'].copy(name='upper assembly plug - xy-16')
xy16Secs['medianAssemblyPlug'] = controlSecs['medianAssemblyPlug'].copy(name='median assembly plug - xy-16')

# 组件钠腔
xy16Secs['lowSodiumGap'] = controlSecs['lowSodiumGap'].copy(name='lower sodium gap - xy-16')
xy16Secs['medianSodiumGap'] = controlSecs['medianSodiumGap'].copy(name='median sodium gap - xy-16')
xy16Secs['upSodiumGap'] = controlSecs['upSodiumGap'].copy(name='upper sodium gap - xy-16')

# 下适配器
xy16Secs['lowAdp-narrow'] = controlSecs['lowAdp-narrow'].copy(name='lower adapter narrow - xy-16')
xy16Secs['lowAdp-trans'] = controlSecs['lowAdp-trans'].copy(name='lower adapter trans - xy-16')
xy16Secs['lowAdp-wide'] = controlSecs['lowAdp-wide'].copy(name='lower adapter narrow - xy-16')

# 包壳端盖
xy16Secs['lowCladPlug'] = controlSecs['lowCladPlug'].copy(name='lower cladding plug - xy-16')
xy16Secs['upCladPlug'] = controlSecs['upCladPlug'].copy(name='upper cladding plug - xy-16')

# 燃料芯块

# 元件钠腔
xy16Secs['sodiumAboveRod'] = controlSecs['sodiumAboveRod'].copy(name='sodium above rod - xy-16')

# 氦气腔
xy16Secs['gasPlenum'] = controlSecs['gasPlenum'].copy(name='gas plenum - xy-16')

# 上部扩展区
xy16Secs['upEx-low'] = controlSecs['upEx-low'].copy(name='lower part of upper extension - xy-16')
xy16Secs['upEx-high'] = controlSecs['upEx-high'].copy(name='higher part of upper extension - xy-16')


# Poison supercell
# loc = '05A02' # assembly used as supercell
# hwcrSecs['poisonSlug'].scSection = buildSec(location=loc, secType='driver', slugMats=slugmat.get(loc))[1]


# Test during development
if __name__ == '__main__':
    def clacNum(r, k):
        if r == 0:
            return k + 1
        elif r == 1:
            return 1 + clacNum(r-1, k)
        else:
            return 6 * (r-1) + clacNum(r-1, k)

    import numpy as np
    lattice = []
    for location, assemblyType, mats in fuelSlugs:
        r, k = slugmat.convertLocation(location)
        lattice.append((clacNum(r, k), location, assemblyType, (r, k)))
    
    lattice = sorted(lattice, key=lambda x: x[0])
    for info in lattice:
        print(info)
