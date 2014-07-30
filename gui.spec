# -*- mode: python -*-

# Configuration
# ----------------------------------------------------------------------------
ONE_FILE = False
PROJECT_PATH = '/Users/besshf/repositories/poissonblending'
OS = ('windows', 'macosx')[1] # 'windows' or 'macosx'
# ----------------------------------------------------------------------------

EXE_FILE_NAME = DIR_NAME = 'PyPoi'
if OS == 'windows':
    EXE_FILE_NAME += '.exe'

a = Analysis(['gui.py'],
             pathex=[PROJECT_PATH],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)

for i in range(1, 4):
    base = 'testimages/test%d' % i
    a.datas += [
        (base + '_src.png', base + '_src.png', 'DATA'),
        (base + '_target.png', base + '_target.png', 'DATA'),
        (base + '_mask.png', base + '_mask.png', 'DATA'),
        ]

# Hack to suppress a warning
# http://stackoverflow.com/questions/19055089/pyinstaller-onefile-warning-pyconfig-h-when-importing-scipy-or-scipy-signal
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break

pyz = PYZ(a.pure)

if ONE_FILE:
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name=EXE_FILE_NAME,
              debug=False,
              strip=None,
              upx=True,
              console=False )
else:
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name=EXE_FILE_NAME,
              debug=False,
              strip=None,
              upx=True,
              console=False )
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=None,
                   upx=True,
                   name=DIR_NAME)
