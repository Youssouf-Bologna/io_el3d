#import python module
import struct

#import blender module
import bpy
import bmesh

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.types import Operator

#import local module
from io_el3D.el3D import el3d_data_obj

def hash_vertex(position):
    return struct.pack("3f",position[0], position[1], position[2])

class ImportE3DFile(Operator, ImportHelper, AddObjectHelper):
    """Importe un fichier 3D de landes eternelles"""
    bl_idname = "import.e3d"  # important since its how bpy.ops.import_e3d.file is constructed
    bl_label = "Import EL3D"

    # ImportHelper mixin class uses this
    filename_ext = ".e3d"

    filter_glob: StringProperty(
        default="*.e3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        filepath = self.filepath

        print("Lecture du fichier ", filepath ,"...")

        f = open(filepath,'rb')
        data = f.read()
        f.close()

        el3d_data = el3d_data_obj.El3dData.load(data)

        #On retire les doublons triplet dans la liste des vectrices
        vertex_dic = {}
        vertex_no = 0
        verts = []
        i=0
        for vertex in el3d_data.vertex_list:
            hash_value = hash_vertex(vertex.position)
            if hash_value not in vertex_dic:
                vertex_dic[hash_value] = vertex_no
                vertex_no += 1
                verts.append(vertex.position)

        faces = []
        for index in range(0, len(el3d_data.index_list), 3):
            face = []
            for i in range(0,3):
                vert_idx = el3d_data.index_list[index + i]
                hash = hash_vertex(el3d_data.vertex_list[vert_idx].position)
                face.append(vertex_dic[hash])
            faces.append(face)

        edges = []

        bmesh = bpy.data.meshes.new(name="New Object Mesh")
        bmesh.from_pydata(verts, edges, faces)

        # uv_layer = bmesh.loops.layers.uv.verify()

        # for face in bmesh.faces:
        #     for loop in face.loops:
        #         loop_uv = loop[uv_layer]
        #         # use xy position of the vertex as a uv coordinate
        #         loop_uv.uv = loop.vert.co.xy
        #
        # bmesh.update_edit_mesh(me)

        object_data_add(context, bmesh, operator=self)

        return {'FINISHED'}
