from .compress import Class as Compress
from . import options as Options

class Class():
	"""class el3d.vertex represente une vectrice el3d """

	def __init__(self, data, header, has_normal, fix_uv = False):
		VO = Options.Vertex
		FO = Options.Format

		data_offset = 0

		self.uv = [0.0]*2
		self.uv[0] = data[0]
		if fix_uv:
			self.uv[1] = data[1]
		else:
			self.uv[1] = 1.0 - data[1]
		data_offset += 2

		if bool(VO.has_extra_uv & header.vertex_options):
			self.extra_uv =  [0.0]*2
			self.extra_uv[0]= data[data_offset]
			if fix_uv:
				self.extra_uv[1]= data[data_offset + 1]
			else:
				self.extra_uv[1]= 1.0 - data[data_offset + 1]
			data_offset += 2
		else: self.has_extra_uv = False

		if has_normal:
			if bool(FO.compressed_normal & header.format_options):
				cpsr = Compress()
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

		if bool(VO.has_tangent & header.vertex_options):
			if bool(FO.compressed_normal & header.format_options):
				cpsr = Compress()
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

		if bool(VO.has_color & header.vertex_options):
			self.color = [0.0] * 3
			(self.color[0],self.color[1] , self.color[2])= data[data_offset:data_offset + 3]
		else: self.color = False
