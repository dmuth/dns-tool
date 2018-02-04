#
# This module holds our parsing code for DNS messages.
#


import binascii
import logging

import parse_answer

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

	if header["opcode"] == 0:
		retval["opcode_text"] = "Standard query"
	elif header["opcode"] == 1:
		retval["opcode_text"] = "Inverse query"
	elif header["opcode"] == 2:
		retval["opcode_text"] = "Server status request"
	else:
		retval["opcode_text"] = "Unknown! (%s)" % header["opcode"]

	if header["aa"] == 0:
		retval["aa"] = "Server isn't an authority"
	elif header["aa"] == 1:
		retval["aa"] = "Server is an authority"
	else:
		retval["aa"] = "Unknown! (%s)" % header["aa"]

	if header["tc"] == 0:
		retval["tc"] = "Message not truncated"
	elif header["tc"] == 1:
		retval["tc"] = "Message truncated"
	else:
		retval["tc"] = "Unknown! (%s)" % header["tc"]

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
		retval["rcode_text"] = "No errors reported"
	elif header["rcode"] == 1:
		retval["rcode_text"] = "Format error (nameserver couldn't interpret this query)"
	elif header["rcode"] == 2:
		retval["rcode_text"] = "Server failure"
	elif header["rcode"] == 3:
		retval["rcode_text"] = "Name error (name does not exist!)"
	elif header["rcode"] == 4:
		retval["rcode_text"] = "Not implemented (nameserver doesn't support this type of query)"
	elif header["rcode"] == 5:
		retval["rcode_text"] = "Refused (the server refused to answer our question!)"
	else:
		retval["rcode_text"] = "Error code %s" % header["rcode"]

	return(retval)


#
# Extract request ID from the header
#
def getRequestId(data):
	retval = binascii.hexlify(data[0:2])
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
	retval["header"]["opcode"] = (ord(data[2]) & 0b01111000) >> 3
	retval["header"]["aa"] = (ord(data[2]) & 0b00000100) >> 2
	retval["header"]["tc"] = (ord(data[2]) & 0b00000010) >> 1
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




