import enum

class Vertex(enum.IntFlag):
	""" Options des vertex """
	has_normal = 1
	has_tangent = 2
	has_extra_uv = 4
	has_color = 8

class Format(enum.IntFlag):
	""" Options de compression/optimisation des formats """
	half_position = 1
	half_uv = 2
	half_extra_uv = 4
	compressed_normal = 8
	short_index = 16
