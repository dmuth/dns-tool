#
# This module holds code which parses the answer body and different types of answers.
#


import struct
import logging
logger = logging

import output
import parse_question


def parseAnswerBody(answer, index, data):
	"""
	parseAnswerBody(answer, index, data): Extract the answer body.

	answer - The data that corresponds to the specific answer
	index - Offset of where we are in the DNS response
	data - The data for the entire answer packet, which is used if there is compression/pointers
	"""

	retval = {}
	retval_text = ""

	if answer["headers"]["type"] == 1:
		(retval, retval_text) = parseAnswerA(answer["rddata_raw"][12:], index, data)

	elif answer["headers"]["type"] == 2:
		#
		# SOA - RFC 1035 3.3.11
		#
		(retval, retval_text) = parseAnswerNs(answer["rddata_raw"][12:], index, data)

	elif answer["headers"]["type"] == 5:
		#
		# SOA - RFC 1035 3.3.1
		#
		(retval, retval_text) = parseAnswerCname(answer["rddata_raw"][12:], index, data)

	elif answer["headers"]["type"] == 6:
		#
		# SOA - RFC 1035 3.3.13
		#
		(retval, retval_text) = parseAnswerSoa(answer["rddata_raw"][12:], index, data)

	elif answer["headers"]["type"] == 15:
		#
		# MX - RFC 1035 3.3.9
		#
		(retval, retval_text) = parseAnswerMx(answer["rddata_raw"][12:], index, data)

	elif answer["headers"]["type"] == 16:
		#
		# MX - RFC 1035 3.3.14
		#
		(retval, retval_text) = parseAnswerTxt(answer["rddata_raw"][12:], index, data)

	elif answer["headers"]["type"] == 28:
		#
		# AAAA - RFC 3596 2.2
		#
		(retval, retval_text) = parseAnswerAAAA(answer["rddata_raw"][12:], index, data)

	else:
		retval["sanity"] = []
		logger.warn("Unknown answer QTYPE: %s" % answer["headers"]["type"])

	#
	# Extract the domain name of the question that this answer points to.
	#
	(retval["question_text"], _, retval["question_meta"]) = parse_question.extractDomainName(index, data)


	return(retval, retval_text)


def parseAnswerA(answer, index, data):
	"""
	parseAnswerA(data): Grab our IP address from an answer to an A query
	"""

	retval = {}

	text = (str(ord(answer[0])) + "." + str(ord(answer[1])) 
		+ "." + str(ord(answer[2])) + "." + str(ord(answer[3])))

	retval["ip"] = text
	#
	# TODO: There may be pointers even for A responses.  Will have to check into this later.
	#
	retval["sanity"] = []

	return(retval, text)


def parseAnswerAAAA(answer, index, data):
	"""
	parseAnswerAAAA(data): Grab our IP address from an answer to an A query
	"""

	retval = {}

	text = output.formatHex(answer, delimiter = ":", group_size = 4)

	retval["ip"] = text
	retval["sanity"] = []

	return(retval, text)


def parseAnswerNs(answer, index, data):
	"""
	parseAnswerNs(answer, data): Parse an NS answer.
	
	answer - The answer body (no headers)
	data - The entire response packet
	
	"""

	retval = {}

	index += 12
	(text, retval["sanity"], retval["meta"]) = parse_question.extractDomainName(index, data)

	return(retval, text)

def parseAnswerCname(answer, index, data):
	"""
	parseAnswerCname(answer, data): Parse a Cname answer.
	
	answer - The answer body (no headers)
	data - The entire response packet
	
	"""

	retval = {}

	index += 12
	(text, retval["sanity"], retval["meta"]) = parse_question.extractDomainName(index, data)

	retval["text"] = text

	return(retval, text)


def parseAnswerTxt(answer, index, data):
	"""
	parseAnswerCname(answer, data): Parse a Cname answer.
	
	answer - The answer body (no headers)
	data - The entire response packet
	
	"""

	retval = {}
	retval["sanity"] = []

	#
	# First byte is the character count, but we already have the exact answer
	# thanks to rdlength, so we can skip that.
	#
	answer = answer[1:]

	text = answer
	retval["text"] = answer

	return(retval, text)


def parseAnswerMx(answer, index, data):
	"""
	parseAnswerMx(answer, data): Parse an MX answer.
	
	answer - The answer body (no headers)
	data - The entire response packet
	
	"""

	retval = {}

	preference = struct.unpack(">H", answer[0:2])[0]
	answer = answer[2:]

	index += 12 + 2
	(exchange, retval["sanity"], retval["meta"]) = parse_question.extractDomainName(index, data)

	retval["preference"] = preference
	retval["exchange"] = exchange

	text = "%s %s" % (preference, exchange)

	return(retval, text)


def parseAnswerSoa(answer, index, data):
	"""
	parseAnswerSoa(answer, index, data): Parse an SOA answer. This usually happens when no record is found.
	
	answer - A string containing just the answer
	index - Offset of where we are within the DNS response
	data - The entire packet
	"""

	retval = {}

	#
	# Skip the header
	#
	index += 12

	(mname, sanity_mname, meta_mname) = parse_question.extractDomainName(index, data)
	index += len(mname) + 2

	#
	# Pull out the domain-name of the mailbox of the person resonsible.
	#
	(rname, sanity_rname, meta_rname) = parse_question.extractDomainName(index, data)

	#
	# Okay, so this requires a little explanation.
	#
	# If the rname doesn't have any pointers in it, then we just note the length
	# and advance the index accordingly.
	#
	# But if the rname does have a pointer in it, the extractDomainName() function
	# will note where the index should be after that first pointer, as that will
	# be the start of the headers.  If that value is present, then that's what
	# the index will be set to.
	#
	index += len(rname) + 2
	if "index_after_first_pointer" in meta_rname:
		index = meta_rname["index_after_first_pointer"]

	#
	# In this case, we're dropping the contents of meta_mname because
	# it should never have a pointer in it.
	#
	retval["meta"] = meta_rname
	retval["sanity"] = sanity_mname + sanity_rname

	#
	# Now point to the start of our serial number and go from there.
	#
	serial = data[index:]

	retval["serial"] = struct.unpack(">L", serial[0:4])[0]
	retval["refresh"] = struct.unpack(">L", serial[4:8])[0]
	retval["retry"] = struct.unpack(">L", serial[8:12])[0]
	retval["expire"] = struct.unpack(">L", serial[12:16])[0]
	retval["minimum"] = struct.unpack(">L", serial[16:20])[0]

	text = "%s %s %d %d %d %d %d" % (mname, rname,
		retval["serial"], retval["refresh"], retval["retry"], retval["expire"], 
		retval["minimum"])

	return(retval, text)

