class Class(Exception):
	def __init__(self, msg_str):
		self.msg = msg_str
	def __repr__(self):
		return repr(self.msg)
