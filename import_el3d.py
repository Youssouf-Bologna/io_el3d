#import python module
import struct
import re

#import blender module
import bpy
import bmesh

from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.types import Operator

#import local module
from . import el3d

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

		el3d_data = el3d.Data.load(data)

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

		#recuperation des info du chemin de fichier
		path = re.search(r"^([\/|\\].+[\/|\\])*(.+?)(\..+)$",filepath)
		base_dir = path.group(1)
		name_file = path.group(2)
		#ext_file = path.group(3) #ne sert pas pour le moment

		#On fait une nouvelle géometrie
		name = name_file
		mesh = bpy.data.meshes.new(name)
		mesh.from_pydata(verts, edges, faces)

		#on rajoute les materiaux en général
		mat_step = []
		i = 0
		for mat in el3d_data.material_list:
			if mat.name not in bpy.data.materials.keys():
				bmat = bpy.data.materials.new(mat.name)
				bmat.use_nodes = True
				btext =  bmat.node_tree.nodes.new('ShaderNodeTexImage')
				btext.image = bpy.data.images.load(base_dir + mat.file, check_existing=True)
				principled_BSDF = bmat.node_tree.nodes.get('Principled BSDF')
				bmat.node_tree.links.new(btext.outputs[0],principled_BSDF.inputs[0])
				principled_BSDF.inputs[7].default_value = 0
				principled_BSDF.inputs[9].default_value = 1
			else: bmat = bpy.data.materials.get(mat.name)

			#ici on ajoute les materiaux as la geomtris
			mesh.materials.append(bmat)

		#on edit la geometrie pour affecter les materiaux aux les faces
		object_data_add(context, mesh, operator=self)
		bpy.ops.object.editmode_toggle() #passage en mode edit

		#on dois passer par un Bmesh
		#le Bmesh est dans un espace memoire different du mesh
		bm  = bmesh.from_edit_mesh(mesh)

		uv_layer = bm.loops.layers.uv.verify()
		il = 0
		im = 0
		mat = el3d_data.material_list[im]
		mat_idx = mesh.materials.find(mat.name)
		for face in bm.faces:
			if il >= mat.start + mat.count:
				im += 1
				mat = el3d_data.material_list[im]
				mat_idx = mesh.materials.find(mat.name)
			#ici on lie le materiel as la face
			face.material_index = mat_idx
			#cette boucle complete la cartes des UV
			for loop in face.loops:
				loop_uv = loop[uv_layer]
				i = el3d_data.index_list[il]
				il += 1
				loop_uv.uv = el3d_data.vertex_list[i].uv

		#finalise le script
		bmesh.update_edit_mesh(mesh) #On actualise le mesh
		bmesh.free() #on libére la memoire prise par le Bmesh
		bpy.ops.object.mode_set(mode="OBJECT") #retour en mode object

		return {'FINISHED'}
