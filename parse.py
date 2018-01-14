#
# This module holds our parsing code for DNS messages.
#


import binascii
import logging


logger = logging.getLogger()


def parseHeaderText(header):
	"""
	parseHeaderText(): Go through our parsed headers, and create text descriptions based on them.
	"""

	retval = {}

	if header["qr"] == 0:
		retval["qr"] = "Question"
	elif header["qr"] == 1:
		retval["qr"] = "Response"
	else:
		retval["qr"] = "Unknown! (%s)" % header["qr"]

	if header["aa"] == 0:
		retval["aa"] = "Server isn't an authority"
	elif header["aa"] == 1:
		retval["aa"] = "Server is an authority"
	else:
		retval["aa"] = "Unknown! (%s)" % header["aa"]

	if header["rd"] == 0:
		retval["rd"] = "Recursion not requested"
	elif header["rd"] == 1:
		retval["rd"] = "Recursion requested"
	else:
		retval["rd"] = "Unknown! (%s)" % header["rd"]

	if header["ra"] == 0:
		retval["ra"] = "Recursion not available"
	elif header["ra"] == 1:
		retval["ra"] = "Recursion available!"
	else:
		retval["ra"] = "Unknown! (%s)" % header["ra"]
	
	if header["rcode"] == 0:
		retval["rcode"] = "No errors reported"
	else:
		retval["rcode"] = "Error code %s" % header["rcode"]

	return(retval)


def parseHeader(data):
	"""
	parseHeader(): Extracts the various fields of our header
	
	Returns a dictionary.
	"""

	retval = {}

	retval["request_id"] = binascii.hexlify(data[0:2])

	#
	# Header flag bits:
	#
	# 0 - QR: 0 if query, 1 if answer
	# 1-4 - Opcode: 0 is standard query, 1 is reverse query, 2 is server status request
	# 5 - AA: Is the answer authoritative?
	# 6 - TC: Has the message been truncated?
	# 7 - RD: Set to 1 when recursion is desired
	# 8 - RA: Is Recursion available on this DNS server?
	# 9-11 - Z: These reserved bits are always set to zero.
	# 12-15 - RCODE: Result Code.  0 for no errors.
	#
	logger.debug("Header Flags: %s: %s %s" % (binascii.hexlify(data[2:4]), bin(ord(data[2])), bin(ord(data[3]))))

	retval["header"] = {}
	retval["header"]["qr"] = (ord(data[2]) & 0b10000000) >> 7
	retval["header"]["aa"] = (ord(data[2]) & 0b01111000) >> 3
	retval["header"]["rd"] = (ord(data[2]) & 0b00000001)
	retval["header"]["ra"] = (ord(data[3]) & 0b10000000) >> 7
	retval["header"]["z"]  = (ord(data[3]) & 0b01110000) >> 4
	retval["header"]["rcode"] = (ord(data[3]) & 0b00001111)
	
	#
	# Create text versions of our header fields
	#
	retval["header_text"] = parseHeaderText(retval["header"])

	retval["num_questions"] = binascii.hexlify(data[4:6])
	retval["num_answers"] = binascii.hexlify(data[6:8])
	retval["num_authority_records"] = binascii.hexlify(data[8:10])
	retval["num_additional_records"] = binascii.hexlify(data[10:12])

	return(retval)


def parseQuestion(data):
	"""
	parseQuestion(): Parse the question part of the data
	"""

	retval = {}
	retval["question"] = ""

	len_orig = len(data)

	#
	# Our answer will be a byte that is a length, then a string.
	# This will repeat until that first byte is zero, at which point we're done.
	#
	while True:

		length = int(ord(data[0]))
		if length == 0:
			data = data[1:]
			break

		#
		# Chop off the first byte and get our question
		#
		data = data[1:]
		string = data[0:length]

		if retval["question"]:
			retval["question"] += "."
		retval["question"] += string

		#
		# Now chop off the string and repeat!
		#
		data = data[length:]

	retval["qtype"] = (256 * ord(data[0])) + ord(data[1])
	retval["qclass"] = (256 * ord(data[2])) + ord(data[3])
	data = data[4:]

	if retval["qtype"] == 1:
		retval["qtype_text"] = "A"

	if retval["qclass"] == 1:
		retval["qclass_text" ] = "IN"

	retval["question_length"] = len_orig - len(data)

	return(retval)


def parseAnswer(data):
	"""
	parseAnswer(): Parse the answer part of the response

	The data passed in is the start of the answer, in the Resource Record format
	"""

	retval = {}

	#
	# RR bytes:
	#
	# 0-1: Bits 2-15 contain the offset to the queston that this answer answers.
	#	I will write code to handle this later.
	# 2-3: Type
	# 4-5: Class
	# 6-7: Unused(?)
	# 8-9: TTL
	# 10-11: RDLENGTH
	# 12+: RDDATA (The answer!)
	#

	retval["qtype"] = (256 * ord(data[2])) + ord(data[3])
	retval["qclass"] = (256 * ord(data[4])) + ord(data[5])

	if retval["qtype"] == 1:
		retval["qtype_text"] = "A"

	if retval["qclass"] == 1:
		retval["qclass_text" ] = "IN"

	retval["ttl"] = (256 * ord(data[8])) + ord(data[9])
	retval["rdlength"] = (256 * ord(data[10])) + ord(data[11])

	answer_end = 12 + retval["rdlength"]

	retval["rddata"] = data[12:answer_end]

	if retval["qtype_text"] == "A":
		# IP Address
		answer = retval["rddata"]
		retval["rddata_text"] = (str(ord(answer[0])) + "." + str(ord(answer[1])) 
			+ "." + str(ord(answer[2])) + "." + str(ord(answer[3])))

	retval["rddata"] = binascii.hexlify(retval["rddata"]).decode("utf-8")

	return(retval)

