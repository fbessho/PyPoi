# -*- mode: python -*-

# Configuration
# ----------------------------------------------------------------------------
ONE_FILE = True
project_path = 'C:\\Users\\nat\\PycharmProjects\\poisson-blending'
# ----------------------------------------------------------------------------

a = Analysis(['gui.py'],
             pathex=[project_path],
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
              name='gui.exe',
              debug=False,
              strip=None,
              upx=True,
              console=True )
else:
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name='gui.exe',
              debug=False,
              strip=None,
              upx=True,
              console=True )
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=None,
                   upx=True,
                   name='gui')
