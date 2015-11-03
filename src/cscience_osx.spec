# -*- mode: python -*-
a = Analysis(['cscience.py','dbconversion.py'],
             pathex=['/Users/fernando/Projects/CScience/src'],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)
resources_tree = Tree('../resources', prefix='resources')
database_tree = Tree('../mongo_osx', prefix='database')
dump_tree = Tree('../database_dump', prefix='database_dump')
components_tree = Tree('cscience/components', prefix='cscience/components')
backend_tree = Tree('cscience/backends', prefix='cscience/backends')
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          resources_tree,
          database_tree,
          dump_tree,
          components_tree,
          backend_tree,
          name='cscience',
          debug=False,
          strip=None,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='cscience.app',
             icon=None)
