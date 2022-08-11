import struct, enum
import hashlib
from . import compress

class el3d_error(Exception):
	def __init__(self, msg_str):
		self.msg = msg_str
	def __repr__(self):
		return repr(self.msg)

class VertexOpts(enum.IntFlag):
	""" Options des vertex """
	has_normal = 1
	has_tangent = 2
	has_extra_uv = 4
	has_color = 8

class FormatOpts(enum.IntFlag):
	""" Options de compression/optimisation des formats """
	half_position = 1
	half_uv = 2
	half_extra_uv = 4
	compressed_normal = 8
	short_index = 16

class BinaryFormat:
	""" class BinaryFormat

		Une boite as outils pour fabriquer les format utilisé par struct pour lire les données
	"""
	BYTE_ORDER = "<"
	HEADER = "4s4B16s10i4B"
	VERTEX_POSITION = "3f"
	VERTEX_HALF_POSITION = "3e"
	VERTEX_NORMAL = VERTEX_TANGENT = "3f"
	VERTEX_COMPRESSED_NORMAL = VERTEX_COMPRESSED_TANGENT = "H"
	VERTEX_UV = VERTEX_EXTRA_UV = "2f"
	VERTEX_HALF_UV = VERTEX_HALF_EXTRA_UV = "2e"
	VERTEX_COLOR = "4B"
	INDEX = "I"
	INDEX_SHORT = "H"
	MATERIAL = "i128s6f4i"
	MATERIAL_EXTRA = "128s"

	def header(): return BinaryFormat.BYTE_ORDER + BinaryFormat.HEADER

	def vertex(vertexOpts, formatOpts):
		""" vertex(vertexOpts, formatOpts) -> string le format binaires d'un vertex suivant les options """
		BF = BinaryFormat
		VO = VertexOpts
		FO = FormatOpts
		vertex_format = BF.BYTE_ORDER
		if bool(FO.half_uv & formatOpts):
			vertex_format += BF.VERTEX_HALF_UV
		else: vertex_format += BF.VERTEX_UV
		if bool(VO.has_extra_uv & vertexOpts):
			if bool(FO.half_extra_uv & formatOpts):
				vertex_format += BF.VERTEX_HALF_EXTRA_UV
			else: vertex_format += BF.VERTEX_EXTRA_UV
		if bool(VO.has_normal & vertexOpts):
			if bool(FO.compressed_normal & formatOpts):
				vertex_format += BF.VERTEX_COMPRESSED_NORMAL
			else: vertex_format += BF.VERTEX_NORMAL
		if bool(VO.has_tangent & vertexOpts):
			if bool(FO.compressed_normal & formatOpts):
				vertex_format += BF.VERTEX_COMPRESSED_TANGENT
			else: vertex_format += BF.VERTEX_TANGENT
		if bool(FO.half_position & formatOpts):
			vertex_format += BF.VERTEX_HALF_POSITION
		else: vertex_format += BF.VERTEX_POSITION
		if bool(VO.has_color & vertexOpts): vertex_format += BF.VERTEX_COLOR
		return vertex_format

	def index(formatOpts):
		""" index(formatOpts) -> string le format des indexs en fonctions des options de format"""
		index_format = BinaryFormat.BYTE_ORDER
		if bool(FormatOpts.short_index & formatOpts):  index_format += BinaryFormat.INDEX_SHORT
		else: index_format += BinaryFormat.INDEX
		return index_format

	def material(vertexOpts):
		""" material(vertexOpts) -> string le format des textures en fonctions des options de vertex. """
		material_format = BinaryFormat.BYTE_ORDER
		if bool(VertexOpts.has_extra_uv & vertexOpts): material_format += BinaryFormat.MATERIAL_EXTRA
		else: material_format += BinaryFormat.MATERIAL
		return material_format

class El3dVertex():
	"""class El3dVectrice represente une vectrice el3d """

	def __init__(self, data, vertexOpts, formatOpts, version):
		VO = VertexOpts
		FO = FormatOpts

		if ((version[0] >= 1) & (version[1] >= 1)):
			has_normal = bool(VO.has_normal & vertexOpts)
			fix_uv = False
		else:
			has_normal = not bool(VO.has_normal & vertexOpts)
			formatOpts = 0
			fix_uv = True

		data_offset = 0

		self.uv = [0.0]*2
		self.uv[0] = data[0]
		if fix_uv:
			self.uv[1] = data[1]
		else:
			self.uv[1] = 1.0 - data[1]
		data_offset += 2

		if bool(VO.has_extra_uv & vertexOpts):
			self.extra_uv =  [0.0]*2
			self.extra_uv[0]= data[data_offset]
			if fix_uv:
				self.extra_uv[1]= data[data_offset + 1]
			else:
				self.extra_uv[1]= 1.0 - data[data_offset + 1]
			data_offset += 2
		else: self.has_extra_uv = False

		if has_normal:
			if bool(FO.compressed_normal & formatOpts):
				cpsr = compress.compressor()
				normal = cpsr.uncompress_normal(data[data_offset])
				data_offset += 1
				self.normal = normal
			else:
				self.normal = [0.0] * 3
				(self.normal[0],
				self.normal[1],
				self.normal[2]
				) = data[data_offset:data_offset + 3]
				data_offset += 3
		else: self.normal = False

		if bool(VO.has_tangent & vertexOpts):
			if bool(FO.compressed_normal & formatOpts):
				cpsr = compress.compressor()
				tangent = cpsr.uncompress_normal(data[data_offset])
				data_offset += 1
				self.tangent = tangent
			else:
				self.tangent = [0.0] * 3
				(self.tangent[0],
				self.tangent[1],
				self.tangent[2]
				) = data[data_offset:data_offset + 3]
				data_offset += 3
		else: self.tangent = False

		# print("data:", data)
		# print("offset:", data_offset)

		self.position = [0.0] * 3
		(self.position[0],
		self.position[1],
		self.position[2]
		)= data[data_offset:data_offset + 3]
		data_offset += 3

		if bool(VO.has_color & vertexOpts):
			self.color = [0.0] * 3
			(self.color[0],self.color[1] , self.color[2])= data[data_offset:data_offset + 3]
		else: self.color = False

class El3dMaterial:
	"""class El3dMAterial represente un material el3d """
	def __init__(self, data, vertexOpts):
		self.options = data[0]
		self.material_name = data[1].decode()
		self.min_x = data[2]
		self.min_y = data[3]
		self.min_z = data[4]
		self.max_x = data[5]
		self.max_y = data[6]
		self.max_z = data[7]
		self.min_index = data[8]
		self.max_index = data[9]
		self.start = data[10]
		self.count = data[11]
		if bool(VertexOpts.has_extra_uv & vertexOpts):
			self.extra_material_name = data[12].decode()

class El3dData():
	"""Class El3dData

	representation et manipulation des données d'un object 3D de Landes Eternelles.

	Propriété:
	----------
	version -> un tupple contenant les 4 nombre de la version
	vertex_options -> un bytes des drapeaux d'options des vertex voir VertexOpts
	format_options -> un bytes des drapeaux de format voir FormatOpts
	vertex_list -> un Tuple

	"""

	MAGIC = "e3dx"
	VERSIONS = ((1, 0, 0, 0), (1, 0, 0, 1), (1, 1, 0, 0))

	def __init__(self):
		self.version = ()
		self.vertex_options = 0
		self.format_options = 0
		self.vertex_list = []
		self.index_list = []
		self.material_list = []

	@classmethod
	def load(cls, data):
		""" charge les données depuis un fichier """
		#On recupère les données de l'entête du ficfier
		binary_format_header = BinaryFormat.header()
		binary_size_header = struct.calcsize(binary_format_header)
		(magic,
		version_1, version_2, version_3, version_4,
		digest,
		header_offset,
		vertex_no, vertex_size, vertex_offset,
		index_no, index_size, index_offset,
		material_no, material_size, material_offset,
		vertex_options, format_options,
		reserved_1, reserved_2
		) = struct.unpack(binary_format_header, data[:binary_size_header])
		version = (version_1, version_2, version_3, version_4)

		#Affiche les info sur la console
		print("magic: ", magic)
		print("version: " , version_1 ,version_2 ,version_3 ,version_4 )
		print("md5: ", digest)
		print("header_offset:", header_offset)
		print("nombre de vertex:", vertex_no)
		print("Taille d'un vertex: ", vertex_size)
		print("nombre d'index: ", index_no)
		print("Taille d'un index: ", index_size)
		print("nombre de material:", material_no)
		print("taille d'un material:", material_size)

		#On verifie la coérence des données
		if magic.decode() != cls.MAGIC: raise el3d_error("Le nombre magic n'est pas juste")
		if version not in cls.VERSIONS : raise el3d_error("la version n'est pas reconnue")

		if digest != hashlib.md5(data[header_offset:]).digest():
			raise el3d_error("le hash n'est pas correct.")

		binary_vertex_format = BinaryFormat.vertex(vertex_options, format_options)
		binary_index_format = BinaryFormat.index(format_options)
		binary_material_foramt = BinaryFormat.material(vertex_options)

		if vertex_size != struct.calcsize(binary_vertex_format):
			raise el3d_error("La taille des Vertex est érronée")
		if index_size != struct.calcsize(binary_index_format):
			raise el3d_error("La taille des index est érronée")
		if material_size != struct.calcsize(binary_material_foramt):
			raise el3d_error("La taille des textures est érronée")

		#On construit et hydrate l'object el3d_data
		el3d_data = El3dData()
		el3d_data.version = version
		el3d_data.vertex_options = vertex_options
		el3d_data.format_options = format_options

		#Hydratation des listes. les listes contienne la representation binaire des objects
		for i in range(vertex_no):
			start = vertex_offset + i * vertex_size
			stop = start + vertex_size
			vertex = El3dVertex(
				struct.unpack(binary_vertex_format, data[start:stop]),
				vertex_options, format_options, version)
			el3d_data.vertex_list.append(vertex)

		for i in range(index_no):
			start = index_offset + i * index_size
			stop = start + index_size
			index_tpl = struct.unpack(binary_index_format,data[start:stop])
			el3d_data.index_list.append(index_tpl[0])

		for i in range(material_no):
			start = material_offset + i * material_size
			stop = start + material_size
			material = El3dMaterial(
				struct.unpack(binary_material_foramt, data[start:stop]),
				vertex_options
			)
			el3d_data.material_list.append(material)

		return el3d_data
