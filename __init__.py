bl_info = {
    "name": "io_el3D",
    "author": "Youssouf Bologna",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Import > Import EL3D",
    "description": "Importe les fichiers 3D de landes éternelles",
    # "warning": "",
    # "doc_url": "",
    # "tracker_url": "",
    "support": 'TESTING',
    "category": "Import-Export"
}

import bpy
from .import_el3d import ImportE3DFile

# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportE3DFile.bl_idname, text="EL3d Import Operator")


# Register and add to the "file selector" menu (required to use F3 search "E3d Import Operator" for quick access).
def register():
    bpy.utils.register_class(ImportE3DFile)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportE3DFile)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_e3d.file('INVOKE_DEFAULT')
