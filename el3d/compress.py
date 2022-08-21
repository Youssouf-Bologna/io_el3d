import sys, struct, string
from types import *
from math import *

class Class:
	SIGN_MASK = 0xe000
	XSIGN_MASK = 0x8000
	YSIGN_MASK = 0x4000
	ZSIGN_MASK = 0x2000

	# middle 6 bits - xbits
	TOP_MASK = 0x1F80

	# lower 7 bits - ybits
	BOTTOM_MASK = 0x007F


	def compress_normal(self, normal):
		result = 0
		tmp = 3 * [0]
		tmp[0] = normal[0]
		tmp[1] = normal[1]
		tmp[2] = normal[2]

		if (tmp[0] < 0):
			result |= self.XSIGN_MASK
			tmp[0] = -tmp[0]

		if (tmp[1] < 0):
			result |= self.YSIGN_MASK
			tmp[1] = -tmp[1]

		if (tmp[2] < 0):
			result |= self.ZSIGN_MASK
			tmp[2] = -tmp[2]

		# project the normal onto the plane that goes through
		# X0=(1,0,0),Y0=(0,1,0),Z0=(0,0,1).
		# on that plane we choose an (projective!) coordinate system
		# such that X0->(0,0), Y0->(126,0), Z0->(0,126),(0,0,0)->Infinity
		# a little slower... old pack was 4 multiplies and 2 adds.
		# This is 2 multiplies, 2 adds, and a divide....

		sum = tmp[0] + tmp[1] + tmp[2]
		if (sum < 1e-6):
			sum = 1.0
			tmp[0] = 0.0
			tmp[1] = 0.0
			tmp[2] = 1.0

		w = 126.0 / sum
		x = long(tmp[0] * w)
		y = long(tmp[1] * w)

		# Now we can be sure that 0<=xp<=126, 0<=yp<=126, 0<=xp+yp<=126
		# however for the sampling we want to transform this triangle
		# into a rectangle.

		if (x >= 64):
			x = 127 - x
			y = 127 - y

		# now we that have xp in the range (0,127) and yp in
		# the range (0,63), we can pack all the bits together

		result |= x << 7
		result |= y

		return long(result)

	def uncompress_normal(self, normal):
		result = [0] * 3
		# if we do a straightforward backward transform
		# we will get points on the plane X0,Y0,Z0
		# however we need points on a sphere that goes through
		# these points. Therefore we need to adjust x,y,z so
		# that x^2+y^2+z^2=1 by normalizing the vector. We have
		# already precalculated the amount by which we need to
		# scale, so all we do is a table lookup and a
		# multiplication
		# get the x and y bits
		x = (normal & self.TOP_MASK) >> 7
		y = normal & self.BOTTOM_MASK

		# map the numbers back to the triangle (0,0)-(0,126)-(126,0)
		if ((x + y) >= 127):
			x = 127 - x
			y = 127 - y

		# do the inverse transform and normalization
		# costs 3 extra multiplies and 2 subtracts. No big deal.
		result[0] = x
		result[1] = y
		result[2] = 126 - x - y

		# set all the sign bits
		if (normal & self.XSIGN_MASK):
			result[0] = -result[0]

		if (normal & self.YSIGN_MASK):
			result[1] = -result[1]

		if (normal & self.ZSIGN_MASK):
			result[2] = -result[2]

		len = sqrt(result[0] * result[0] + result[1] * result[1] + result[2] * result[2])
		result[0] /= len
		result[1] /= len
		result[2] /= len
		return result

	def to_float(self, value):
		tmp = struct.pack('<I', long(value))
		return struct.unpack('<f', tmp)[0]

	def half_to_int_float(self, value):
		sign = (long(value) >> 15) & 0x00000001;
		exponent = (long(value) >> 10) & 0x0000001f;
		mantissa =  long(value) & 0x000003ff;

		if (exponent == 0):
			if (mantissa == 0):
				return int(sign << 31)
			else:
				while ((mantissa & 0x00000400) == 0):
					mantissa <<= 1;
					exponent -=  1;

				exponent += 1;
				mantissa &= ~0x00000400;
		else:
			if (exponent == 31):
				if (mantissa == 0):
					return long((sign << 31) | 0x7f800000)
				else:
					return long((sign << 31) | 0x7f800000 | (mantissa << 13))

		exponent += (127 - 15);
		mantissa <<= 13;

		return long((sign << 31) | (exponent << 23) | mantissa)

	def half_to_float(self, value):
		return self.to_float(self.half_to_int_float(long(value)))

	def to_int_float(self, value):
		tmp = struct.pack('<f', value)
		return long(struct.unpack('<I', tmp)[0])

	def int_float_to_half(self, value):
		sign = (long(value) >> 31) & 0x1
		exponent = (long(value) >> 23) & 0xFF
		mantissa = long(value) & 0x7FFFFF

		if (exponent == 0):
			mantissa = 0
			exponent = 0
		else:
			if (exponent == 0xff):
				# NaN or INF
				if (mantissa != 0):
					mantissa = 1
				else:
					mantissa = 0
				exponent = 31
			else:
				# regular number
				new_exponent = exponent - 127

				if (new_exponent < -24):
					# this maps to 0
					mantissa = 0
					exponent = 0
				else:
					if (new_exponent < -14):
						# this maps to a denorm
						exponent = 0
						exponent_value = -14 - new_exponent  # 2^-exp_val

						if (exponent_value == 0):
							mantissa = 0
						elif (exponent_value == 1):
							mantissa = 512 + (mantissa >> 14)
						elif (exponent_value == 2):
							mantissa = 256 + (mantissa >> 15)
						elif (exponent_value == 3):
							mantissa = 128 + (mantissa >> 16)
						elif (exponent_value == 4):
							mantissa = 64 + (mantissa >> 17)
						elif (exponent_value == 5):
							mantissa = 32 + (mantissa >> 18)
						elif (exponent_value == 6):
							mantissa = 16 + (mantissa >> 19)
						elif (exponent_value == 7):
							mantissa = 8 + (mantissa >> 20)
						elif (exponent_value == 8):
							mantissa = 4 + (mantissa >> 21)
						elif (exponent_value == 9):
							mantissa = 2 + (mantissa >> 22)
						elif (exponent_value == 10):
							mantissa = 1
					else:
						if (new_exponent > 15):
							# map this value to infinity
							mantissa = 0
							exponent = 31
						else:
							exponent = new_exponent + 15
							mantissa = mantissa >> 13

		return long((sign << 15) | (exponent << 10) | mantissa)

	def float_to_half(self, value):
		return long(self.int_float_to_half(self.to_int_float(value)))
