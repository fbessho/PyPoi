# -*- mode: python -*-
a = Analysis(['gui.py'],
             pathex=['C:\\Users\\nat\\PycharmProjects\\poisson-blending'],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)
a.datas += [
    ('testimages/test1_src.png',
    './testimages/test1_src.png',
    'DATA'),
    ('testimages/test1_target.png',
    'testimages/test1_target.png','DATA')
    ]
pyz = PYZ(a.pure)
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
