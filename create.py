#
# This module holds functions which are used to create our DNS requests.
#

import logging
import math
import random


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



def createHeader():
	"""createHeader(): Create a header for our question

	"""
	retval = ""

	#
	# The request ID is two bytes, so grab each byte, turn it into a char/string,
	# and append it to the request ID.
	#
	request_id = random.randint(0, 65535)
	request_id1 = request_id >> 8
	request_id2 = request_id & 0xff
	retval += chr(request_id1) + chr(request_id2)

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
	retval += chr(flags[0]) + chr(flags[1])


	# QDCOUNT - Number of questions
	qdcount = 1
	retval += convertTo16Bit(qdcount)

	# ANCOUNT - Number of answer
	retval += convertTo16Bit(0)

	# NSCOUNT - Number of authority records
	retval += convertTo16Bit(0)

	# ARCOUNT - Number of additional records
	retval += convertTo16Bit(0)

	return(retval)


def createQuestion(q, query_type):
	"""createQuestion(q, query_type): Create the question part of our query

	"""

	retval = ""

	#
	# Split up our query, go through each part of it, 
	# and add the len and characters onto the question.
	#
	parts = q.split(".")

	for part in parts:
		retval += chr(len(part)) + part

	#
	# End the question with a zero.
	#
	retval += chr(0)

	if query_type in query_types:
		qtype = query_types[query_type]
	else:
		raise Exception("Unknown query_type: %s" % query_type)

	retval += convertTo16Bit(qtype)

	# QCLASS - 1 is IN
	qclass = 1
	retval += convertTo16Bit(qclass)

	return(retval)


