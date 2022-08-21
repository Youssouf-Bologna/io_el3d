from . import options

class Class:
	""" class el3d.binary_format

		Une boite as outils pour fabriquer les formats utilisés par struct pour lire les données
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

	def header(): return Class.BYTE_ORDER + Class.HEADER

	def vertex(header):
		""" vertex(header) -> string le format binaires d'un vertex suivant les options """
		BF = Class
		VO = options.Vertex
		FO = options.Format

		vertex_format = BF.BYTE_ORDER
		if bool(FO.half_uv & header.format_options):
			vertex_format += BF.VERTEX_HALF_UV
		else: vertex_format += BF.VERTEX_UV
		if bool(VO.has_extra_uv & header.vertex_options):
			if bool(FO.half_extra_uv & header.format_options):
				vertex_format += BF.VERTEX_HALF_EXTRA_UV
			else: vertex_format += BF.VERTEX_EXTRA_UV
		if bool(VO.has_normal & header.vertex_options):
			if bool(FO.compressed_normal & header.format_options):
				vertex_format += BF.VERTEX_COMPRESSED_NORMAL
			else: vertex_format += BF.VERTEX_NORMAL
		if bool(VO.has_tangent & header.vertex_options):
			if bool(FO.compressed_normal & header.format_options):
				vertex_format += BF.VERTEX_COMPRESSED_TANGENT
			else: vertex_format += BF.VERTEX_TANGENT
		if bool(FO.half_position & header.format_options):
			vertex_format += BF.VERTEX_HALF_POSITION
		else: vertex_format += BF.VERTEX_POSITION
		if bool(VO.has_color & header.vertex_options): vertex_format += BF.VERTEX_COLOR
		return vertex_format

	def index(header):
		""" index(header) -> string le format des indexs en fonctions des options de format"""
		index_format = Class.BYTE_ORDER
		if bool(options.Format.short_index & header.format_options):  index_format += Class.INDEX_SHORT
		else: index_format += Class.INDEX
		return index_format

	def material(header):
		""" material(header) -> string le format des textures en fonctions des options de vertex. """
		material_format = Class.BYTE_ORDER
		if bool(options.Vertex.has_extra_uv & header.vertex_options): material_format += Class.MATERIAL_EXTRA
		else: material_format += Class.MATERIAL
		return material_format
