class Class:
	""" class el3d.header represente les header d'un fichier e3d """
	def __init__(self,data=False):
		if data:
			(self.magic,
			version_1, version_2, version_3, version_4,
			self.digest,
			self.offset,
			self.vertex_no, self.vertex_size, self.vertex_offset,
			self.index_no, self.index_size, self.index_offset,
			self.material_no, self.material_size, self.material_offset,
			self.vertex_options, self.format_options,
			self.reserved_1, self.reserved_2
			)= data
			self.version = (version_1, version_2, version_3, version_4)
		else:
			self.magic = b'e3dx'
			self.version = False
			self.digest = False
			self.offset = 28
			self.vertex_no = self.vertex_size = self.vertex_offset = False
			self.index_no = self.index_size = self.index_offset = False
			self.material_no = self.material_size = self.material_offset = False
			self.vertex_options = self.format_options = False
			self.reserved_1 = self.reserved_2 = False
