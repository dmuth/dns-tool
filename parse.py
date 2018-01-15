#
# This module holds our parsing code for DNS messages.
#


import binascii
import logging
import struct


logger = logging.getLogger()

qtypes = {
	1: "A (Address)",
	2: "NS (Nameserver)",
	3: "MD (Mail Destination - Obseleted by MX)",
	4: "MF (Mail Forwarder - Obseleted by MX)",
	5: "CNAME (Canocial Name for an alias)",
	6: "SOA (Start of a zone of Authority)",
	7: "MB (Mailbox Domain Name - experimental)",
	8: "MG (Mail Group Member - experimental)",
	9: "MR (Mail Rename Group Name - experimental)",
	10: "NULL (A null Resource Record - experimental)",
	11: "WKS (A well known service description)",
	12: "PTR (A domain name pointer)",
	13: "HINFO (Host information)",
	14: "MINFO (Mailbox or mail list information)",
	15: "MX (Mail Exchange)",
	16: "TXT (Text string)",
	252: "AXFR (Request for zone transfer)",
	253: "MAILB (Request for mailbox-related records)",
	254: "MAILA (Request for mail agent RRs - obseleted by MX)",
	255: "* (A request for all records)",
	}


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
		retval["opcode"] = "Standard query"
	elif header["opcode"] == 1:
		retval["opcode"] = "Inverse query"
	elif header["opcode"] == 2:
		retval["opcode"] = "Server status request"
	else:
		retval["opcode"] = "Unknown! (%s)" % header["opcode"]

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
		retval["rcode"] = "No errors reported"
	elif header["rcode"] == 1:
		retval["rcode"] = "Format error (nameserver couldn't interpret this query)"
	elif header["rcode"] == 2:
		retval["rcode"] = "Server failure"
	elif header["rcode"] == 3:
		retval["rcode"] = "Name error (name does not exist!)"
	elif header["rcode"] == 4:
		retval["rcode"] = "Not implemented (nameserver doesn't support this type of query)"
	elif header["rcode"] == 5:
		retval["rcode"] = "Refused (the server refused to answer our question!)"
	else:
		retval["rcode"] = "Error code %s" % header["rcode"]

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


def parseQtype(qtype, question = False):
	"""
	parseQtype(qtype): Get a text label for our qtype
	"""

	if qtype in qtypes:
		retval = qtypes[qtype]

	else:
		retval = "Unknown! (%s)" % qtype

	#
	# Sanity check: types of >= 252 are only acceptable for questions, not answers.
	#
	if qtype >= 252 and (not question):
		retval = "Got TYPE >= 252 for non-question. (%s)" % qtype

	return(retval)


def parseQclass(qclass):
	"""
	parseQclass(qclass): Get a text label for our class
	"""

	if qclass == 1:
		retval = "IN"
	else:
		retval = "Unknown! (%s)" % qclass

	return(retval)


def extractDomainName(data):
	"""
	extractDomainName(data) - Extract a domain-name as defined in RFC 1035 3.3
	
	In more detail, this function takes a string which consists of 1 or more bytes
	which indicate length, followed by a string.  It is terminated by a byte
	of value 0x00.
	"""

	retval = ""
	offset = 0

	while True:

		length = int(ord(data[0]))
		offset += 1

		if length == 0:
			data = data[1:]
			break

		#
		# Chop off the first byte and get our question
		#
		data = data[1:]
		string = data[0:length]

		if retval:
			retval += "."
		retval += string

		#
		# Now chop off the string and repeat!
		#
		data = data[length:]
		offset += length

	return(retval, offset)



def parseQuestion(data):
	"""
	parseQuestion(): Parse the question part of the data
	"""

	retval = {}
	retval["question"] = ""

	len_orig = len(data)

	(retval["question"], domain_offset) = extractDomainName(data)
	data = data[domain_offset:]

	retval["qtype"] = (256 * ord(data[0])) + ord(data[1])
	retval["qclass"] = (256 * ord(data[2])) + ord(data[3])
	data = data[4:]

	retval["qtype_text"] = parseQtype(retval["qtype"], question = True)
	retval["qclass_text"] = parseQclass(retval["qclass"])

	retval["question_length"] = len_orig - len(data)

	return(retval)



def parseAnswerIp(data):
	"""
	parseAnswerIp(data): Grab our IP address from an answer to an A query
	"""

	rddata = {}

	text = (str(ord(data[0])) + "." + str(ord(data[1])) 
		+ "." + str(ord(data[2])) + "." + str(ord(data[3])))

	rddata["ip"] = text

	return(rddata, text)


def parseAnswerSoa(data):
	"""
	parseAnswerSoa(data): Grab our SOA record from the answer to a query
	"""

	rddata = {}

	mname, offset = extractDomainName(data)
	data = data[offset:]

	rname, offset = extractDomainName(data)
	data = data[offset:]

	rddata["serial"] = struct.unpack(">L", data[0:4])[0]
	rddata["refresh"] = struct.unpack(">L", data[4:8])[0]
	rddata["retry"] = struct.unpack(">L", data[8:12])[0]
	rddata["expire"] = struct.unpack(">L", data[12:16])[0]
	rddata["minimum"] = struct.unpack(">L", data[16:20])[0]

	text = "%s %s %d %d %d %d %d" % (mname, rname, 
		rddata["serial"], rddata["refresh"], rddata["retry"], rddata["expire"], 
		rddata["minimum"])

	return(rddata, text)

def parseAnswerMx(data):
	"""
	parseAnswerMx(data): Grab or MX record from the answer to a query.
	"""

	rddata = {}

	preference = struct.unpack(">H", data[0:2])[0]
	data = data[2:]

	exchange, offset = extractDomainName(data)

	rddata["preference"] = preference
	rddata["exchange"] = exchange

	text = "%s %s" % (preference, exchange)

	return(rddata, text)


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

	retval["qtype_text"] = parseQtype(retval["qtype"])
	retval["qclass_text"] = parseQclass(retval["qclass"])

	retval["ttl"] = (256 * ord(data[8])) + ord(data[9])
	retval["rdlength"] = (256 * ord(data[10])) + ord(data[11])

	answer_end = 12 + retval["rdlength"]

	retval["rddata_raw"] = data[12:answer_end]

	if retval["qtype"] == 1:
		# IP Address
		(retval["rddata"], retval["rddata_text"]) = parseAnswerIp(retval["rddata_raw"])

	elif retval["qtype"] == 6:
		#
		# SOA - RFC 1035 3.3.13
		#
		(retval["rddata"], retval["rddata_text"]) = parseAnswerSoa(retval["rddata_raw"])

	elif retval["qtype"] == 15:
		#
		# MX - RFC 1035 3.3.9
		#
		(retval["rddata"], retval["rddata_text"]) = parseAnswerMx(retval["rddata_raw"])


	retval["rddata_hex"] = binascii.hexlify(retval["rddata_raw"]).decode("utf-8")
	del retval["rddata_raw"]

	return(retval)

