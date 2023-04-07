"""
Divide TULIP input card into several cards

Author: LZK
Date: 2023-2-21
"""
import os
import shutil
from getpass import getuser

WORK_PATH = {
    '12247': 'G:\Research\Research\Projects\LoongSARAXVerif\code\model_ver2', 
    'Zikang Li': 'C:\\SJTUGraduate\\Research\\Projects\\LoongSARAXVerif\\code\\model_ver2',
    'admin':  'C:\\SJTUGraduate\\Research\\Projects\\LoongSARAXVerif\\code\\model_ver2'
}

CARD_PATH = os.path.join(WORK_PATH[getuser()], 'output', 'TPmate.inp')


class GeomKind:

    def __init__(self, string) -> None:
        self.string = string
        self.kinds = list()
        self.values = list()
    
    def parse(self):
        if 'geom_kind' in self.string:
            kindStrs = self.string.split()[1:]
        else:
            kindStrs = self.string.split()
        for kindStr in kindStrs:
            if '*' in kindStr:
                value, kind = kindStr.split('*')
            else:
                value = 1
                kind = kindStr
            self.values.append(int(value))
            self.kinds.append(kind)
    
    def __sub__(self, rvalue):
        for idx in range(len(self.values)):
            if self.values[idx] > 0:
                self.values[idx] -= rvalue
                break
    
    def pop(self, num):
        ret = []
        for _ in range(num):
            for idx in range(len(self.kinds)):
                if self.values[idx] > 0:
                    ret.append(self.kinds[idx])
                    self.values[idx] -= 1
                    break
        
        s = ['{}'.format(ret[0])]
        for retKind in ret[1:]:
            num, kind = int(s[-1].split('*')[0]), s[-1].split('*')[-1]
            if kind == retKind:
                if '*' not in s[-1]:
                    s[-1] = '2*{}'.format(retKind)
                else:
                    s[-1] = '{:d}*{}'.format(num+1, retKind)
            else:
                s.append('{}'.format(retKind))
        
        return ' '.join(s)

    def __str__(self) -> str:
        ret = list()
        for kind, value in zip(self.kinds, self.values):
            if value > 0:
                ret.append('{:d}*{}'.format(value, kind))
        
        return '{:<22}{:<8}{:<8}{:<8}'.format('geom_kind', *ret)


def divideGeometry(card) -> list:
    return card.split('\n\n\n')


def control2dict(card) -> dict:
    lines = card.split('\n')
    ret = dict()
    for idx in range(len(lines)):
        if ' ' not in lines[idx] or '!' in lines[idx]:
            continue
        keyword, value = lines[idx][:22].rstrip(' '), lines[idx][22:]
        ret[keyword] = value
    
    return ret


def dict2control(controlDict) -> str:
    assert type(controlDict) is dict
    s = list()
    for k, v in controlDict.items():
        s.append('{:<22}{}'.format(k, v))
    
    return '\n'.join(s)


def generateCard(info, header, control, geometry, materials, geom_kind, jobName):
    assert type(info) is dict
    assert type(header) is str
    assert type(control) is dict
    assert type(geometry) is list
    assert type(materials) is str

    # Modify the control
    control['n_mat'] = len(geometry)
    control['geom_kind'] = geom_kind

    # Re-arrange the sections
    for newId, section in enumerate(geometry):
        lines = section.split('\n')
        for lineIdx in range(len(lines)):
            if 'mat' in lines[lineIdx] and '_' not in lines[lineIdx]:
                lines[lineIdx] = 'mat{:d}'.format(newId+1)
        geometry[newId] = '\n'.join(lines)

    # Add information into header
    header = '! MAT{:d}-{:d} created by divider.py\n'.format(info['startId'], info['endId']) + header

    # Merge sub-cards into TPmate.inp
    card = header + '\n\nCONTROL:\n' + dict2control(control)\
                  + '\n\nGEOMETRY:\n' + '\n\n'.join(geometry)\
                  + '\n\nMATERIAL:\n' + materials

    # Save the new card in path "./@JOB_NAME/matXXX-YYY/TPmate.inp"
    path = os.path.join(os.getcwd(), jobName, "mat{:d}-{:d}".format(info['startId'], info['endId']))
    if not os.path.exists(path):
        os.mkdir(path)
    with open(os.path.join(path, 'TPmate.inp'), 'w', encoding='utf-8') as f:
        f.write(card)

    # Auxiliary file
    with open(os.path.join(path, 'info.txt'), 'w', encoding='utf-8') as f:
        f.write('{:<10}{:d}\n'.format('startId', info['startId']))
        f.write('{:<10}{:d}'.format('endId', info['endId']))
        # f.write('{:<10}{:d}'.format())


def generateShell(info, jobName):
    cwd = os.getcwd()
    matId = "mat{:d}-{:d}".format(info['startId'], info['endId'])
    path = os.path.join(cwd, jobName, matId)
    for shellFile in ('env.sh', 'jobsubmit.sh', 'loongsarax.sh'):
        shutil.copy(os.path.join(cwd, shellFile), os.path.join(path, shellFile))
    
    # Replace tags in loongsarax.sh
    loongsaraxText = str()
    with open(os.path.join(path, 'loongsarax.sh'), 'r', encoding='utf-8') as loongsarax:
        loongsaraxText = loongsarax.read()
        loongsaraxText = loongsaraxText.replace('@JOB_NAME', jobName)
        # loongsaraxText.replace('@BATCH_NAME', )
        loongsaraxText = loongsaraxText.replace('@MAT_ID', matId)
    
    with open(os.path.join(path, 'loongsarax.sh'), 'w', encoding='utf-8') as loongsarax:
        loongsarax.write(loongsaraxText)

    # Replace tags in jobsubmit.sh
    jobsubmitText = str()
    with open(os.path.join(path, 'jobsubmit.sh'), 'r', encoding='utf-8') as jobsubmit:
        jobsubmitText = jobsubmit.read()
        jobsubmitText = jobsubmitText.replace('@JOB_NAME', jobName)
        # jobsubmitText.replace('@BATCH_NAME', )
        jobsubmitText = jobsubmitText.replace('@MAT_ID', matId)
    
    with open(os.path.join(path, 'jobsubmit.sh'), 'w', encoding='utf-8') as jobsubmit:
        jobsubmit.write(jobsubmitText)


def divide(jobName, cardPath, batchSize):
    # Read in TULIP input card
    with open(cardPath, 'r', encoding='utf-8') as f:
        card = f.read()

    # Divide into cards
    header, remains = card.split('CONTROL:')
    control, remains = remains.split('GEOMETRY:')
    geometry, materials = remains.split('MATERIAL:')

    # Divide the geometry card
    geometry = divideGeometry(geometry)

    # Turn the control card into dict
    control = control2dict(control)

    # Garantee geom_kind matches mat
    gk = GeomKind(string=control['geom_kind'])
    gk.parse()

    # Allocate geometry & Generate cards
    for batchId in range(len(geometry) // batchSize + int(bool(len(geometry) % batchSize))):
        info = {
            'cardId': batchId,
            'startId': batchId * batchSize + 1,
            'endId': min((batchId + 1) * batchSize, len(geometry)-1)
        }
        geom_kind = gk.pop(num=batchSize)
        generateCard(
            info=info,
            header=header,
            control=control,
            geometry=geometry[info['startId']-1:info['endId']],
            materials=materials,
            geom_kind=geom_kind,
            jobName=jobName
        )
        
        # generateShell(info=info, jobName=jobName)


if __name__ == '__main__':
    divide(jobName='div_0407', cardPath=CARD_PATH, batchSize=50)

