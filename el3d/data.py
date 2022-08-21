import struct
import hashlib
from .error import Class as Error
from .binary_format import Class as BinaryFormat
from .header import Class as Header
from .vertex import Class as Vertex
from .material import Class as Material
from . import options as Options

class Class():
	"""Class El3dData

	representation et manipulation des données d'un object 3D de Landes Eternelles.

	Propriété:
	----------
	header -> l'entête de ficher
	vertex_list -> la liste des vertex
	index_list -> la liste des index
	material_list -> la liste des materiaux

	"""

	MAGIC = "e3dx"
	VERSIONS = ((1, 0, 0, 0), (1, 0, 0, 1), (1, 1, 0, 0))

	def __init__(self):
		self.header = False
		self.vertex_list = []
		self.index_list = []
		self.material_list = []

	@classmethod
	def load(cls, data):
		""" charge les données depuis un fichier """
		#On recupère les données de l'entête du ficfier
		binary_format_header = BinaryFormat.header()
		binary_size_header = struct.calcsize(binary_format_header)
		header = struct.unpack(binary_format_header, data[:binary_size_header])

		#On construit et hydrate l'object el3d_data
		el3d_data = cls()
		el3d_data.header = Header(header)

		binary_vertex_format = BinaryFormat.vertex(el3d_data.header)
		binary_index_format = BinaryFormat.index(el3d_data.header)
		binary_material_foramt = BinaryFormat.material(el3d_data.header)

		#On verifie la coérence des données
		if el3d_data.header.magic.decode() != cls.MAGIC:
			raise Error("Le nombre magic n'est pas juste")
		if el3d_data.header.version not in cls.VERSIONS :
			raise Error("la version n'est pas reconnue")

		if el3d_data.header.digest != hashlib.md5(data[el3d_data.header.offset:]).digest():
			raise Error("le hash n'est pas correct.")

		if el3d_data.header.vertex_size != struct.calcsize(binary_vertex_format):
			raise Error("La taille des Vertex est érronée")
		if el3d_data.header.index_size != struct.calcsize(binary_index_format):
			raise Error("La taille des index est érronée")
		if el3d_data.header.material_size != struct.calcsize(binary_material_foramt):
			raise Error("La taille des textures est érronée")

		#fix_uv & particularité de version
		if ((el3d_data.header.version[0] >= 1) & (el3d_data.header.version[1] >= 1)):
			has_normal = bool(Options.Vertex.has_normal & el3d_data.header.vertex_options)
			fix_uv = False
		else:
			has_normal = not bool(Options.Vertex.has_normall & el3d_data.header.vertex_options)
			el3d_data.header.format_options = 0
			fix_uv = True

		#Hydratation des listes.
		no = el3d_data.header.vertex_no
		offset = el3d_data.header.vertex_offset
		size = el3d_data.header.vertex_size
		for i in range(no):
			start = offset + i * size
			stop = start + size
			vertex = Vertex(
				struct.unpack(binary_vertex_format, data[start:stop]),
				el3d_data.header, has_normal, fix_uv)
			el3d_data.vertex_list.append(vertex)

		no = el3d_data.header.index_no
		offset = el3d_data.header.index_offset
		size = el3d_data.header.index_size
		for i in range(no):
			start = offset + i * size
			stop = start + size
			index = struct.unpack(binary_index_format,data[start:stop])[0]
			el3d_data.index_list.append(index)

		no = el3d_data.header.material_no
		offset = el3d_data.header.material_offset
		size = el3d_data.header.material_size
		for i in range(no):
			start = offset + i * size
			stop = start + size
			material = Material(
				struct.unpack(binary_material_foramt, data[start:stop]),
				el3d_data.header)
			el3d_data.material_list.append(material)

		return el3d_data
