# -*- mode: python -*-
import platform
import os

# Configuration
# ----------------------------------------------------------------------------
__VERSION__ = '0.2.0'
ONE_FILE = os.environ.get('PYPOI_BUILD_ONE_FILE', "") == 'yes'
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
OS = platform.system().lower()
# ----------------------------------------------------------------------------

logger.info('== Configuration ==')
logger.info('OS: %s', OS)
logger.info('Mode: %s', 'one file mode' if ONE_FILE else 'multiple file mode')
logger.info('Project Path: %s', PROJECT_PATH)

# Specify dir/file names
DIR_NAME = 'PyPoi-%s-%s' % (__VERSION__, OS)
EXE_FILE_NAME = 'PyPoi'
if ONE_FILE:
    EXE_FILE_NAME += '-%s-%s' % (__VERSION__, OS)
if OS == 'windows':
    EXE_FILE_NAME += '.exe'

a = Analysis(['pypoi\gui.py'],
             pathex=[PROJECT_PATH],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)

for i in range(1, 5):
    base = 'pypoi/testimages/test%d' % i
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
