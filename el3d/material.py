import re
from . import options

class Class:
	"""class el3d.material represente un material el3d """
	def __init__(self, data, header):
		self.options = data[0]
		self.file = data[1].decode()
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
		if bool(options.Vertex.has_extra_uv & header.vertex_options):
			self.extra_file= data[12].decode()
		else: self.extra_file = False
		self.name = self.file.split(".",1)[0]
