#
# This module holds functions which are used to create our DNS requests.
#

import logging
import math
import random
import struct


logger = logging.getLogger()


#
# A lookup table for our query types.
#
query_types = {
	"a": 1,
	"ns": 2,
	"md": 3,
	"mf": 4,
	"cname": 5,
	"soa": 6,
	"mb": 7,
	"mg": 8,
	"mr": 9,
	"null": 10,
	"wks": 11,
	"ptr": 12,
	"hinfo": 13,
	"minfo": 14,
	"mx": 15,
	"txt": 16,
	"aaaa": 28,
	"axfr": 252,
	"mailb": 253,
	"maila": 254,
	"*": 255,
	}


def convertTo16Bit(val):
	"""
	convertTo16Bit(val): Convert an integer into a 16-bit value

	I'm honestly a bit rusty on how to "best" do this, so now I'm going to do it by hand.
	"""

	retval = ""

	if val < 256:
		retval = chr(0) + chr(val)

	elif val < 65536:
		ret1 = int(math.floor(val / 256))
		ret2 = val % 256
		retval = chr(ret1) + chr(ret2)

	else:
		raise Exception("Value %s is too large for a 16-bit int!" % val)

	return(retval)



def createHeader(args):
	"""createHeader(args): Create a header for our question

	An array of bytes is returned.

	"""

	retval = bytes()

	if args.request_id:
		#
		# If the request ID is specified on the command line, parse the hex string.
		#
		request_id = int(args.request_id, 16)
		if request_id > 65535:
			raise Exception("Request ID of '%s' (%d) is over 65535!" % (
				args.request_id, request_id))

	else:
		request_id = random.randint(0, 65535)


	#
	# The request ID is two bytes, so grab each byte, turn it into a char/string,
	# and append it to the retval.
	#
	request_id1 = request_id >> 8
	request_id2 = request_id & 0xff
	retval += struct.pack("B", request_id1) + struct.pack("B", request_id2)

	# Flags
	flags = [0, 0]

	#
	# Opcode: 0 = standard query, 1 = inverse query, 2 = server status request
	#
	opcode = 0

	#
	# TODO:
	# - Add support for setting opcode in flags[0]
	# - Add support for TC in flags[0]
	# 

	# Recursion desired?
	rd = 1
	flags[0] |= rd

	#
	# Add in our header
	#
	retval += struct.pack("B", flags[0]) + struct.pack("B", flags[1])


	# QDCOUNT - Number of questions
	qdcount = 1
	retval += struct.pack(">H", qdcount)

	# ANCOUNT - Number of answer
	retval += struct.pack(">H", 0)

	# NSCOUNT - Number of authority records
	retval += struct.pack(">H", 0)

	# ARCOUNT - Number of additional records
	retval += struct.pack(">H", 0)

	return(retval)


def createQuestion(q, query_type):
	"""createQuestion(q, query_type): Create the question part of our query

	An array of bytes is returned.

	"""

	retval = bytes()

	#
	# Split up our query, go through each part of it, 
	# and add the len and characters onto the question.
	#
	parts = q.split(".")

	for part in parts:
		retval += struct.pack("B", len(part))
		retval += struct.pack("%ds" % len(part), bytes(part, "utf-8"))

	#
	# End the question with a zero.
	#
	retval += struct.pack("B", 0)

	if query_type in query_types:
		qtype = query_types[query_type]
	else:
		raise Exception("Unknown query_type: %s" % query_type)

	retval += struct.pack(">H", qtype)

	# QCLASS - 1 is IN
	qclass = 1
	retval += struct.pack(">H", qclass)

	return(retval)


