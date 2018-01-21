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
	28: "AAAA (Ipv6 Address)",
	252: "AXFR (Request for zone transfer)",
	253: "MAILB (Request for mailbox-related records)",
	254: "MAILA (Request for mail agent RRs - obseleted by MX)",
	255: "* (A request for all records)",
	}


def formatHex(data, delimiter = " ", group_size = 2):
	"""
	formatHex(data, delimiter = " ", group_size = 2): Returns a nice hex version of a string

	data - The string to turn into hex values
	delimiter - The delimter between hex values
	group_size - How many characters do we want in a group?
	"""

	# Python 2
	hex = binascii.hexlify(data)
	retval = delimiter.join(hex[i:i + group_size] for i in range(0, len(hex), group_size))

	# Python 3
	#if not isinstance(data, bytes):
	#	hex = bytearray(data, "iso8859-1").hex()
	#else:
	#	hex = data.hex()
	#
	#retval = delimiter.join(hex[i:i + group_size] for i in range(0, len(hex), group_size))

	return(retval)


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


def parseQuestion(index, data):
	"""
	parseQuestion(): Parse the question part of the data
	"""

	retval = {}
	retval["question"] = ""

	len_orig = len(data)
	index_start = index

	#
	# The domain-name in the question is in the same format as it is in the answer.
	# So I have that going for me which is nice.
	# The offset can be calculated by adding 2 the value we extract, 1 byte for the leading
	# length byte and 1 byte for the final 0x00.
	#
	(retval["question"], _, _) = extractDomainName(index, data)
	index += len(retval["question"]) + 2

	#
	# Now pull out the QTYPE and QCLASS.
	#
	data = data[index:]

	retval["qtype"] = (256 * ord(data[0])) + ord(data[1])
	retval["qclass"] = (256 * ord(data[2])) + ord(data[3])
	data = data[4:]

	retval["qtype_text"] = parseQtype(retval["qtype"], question = True)
	retval["qclass_text"] = parseQclass(retval["qclass"])

	index += 4

	retval["question_length"] = index - index_start

	return(retval)


def getPointerAddress(data):
	"""
	getPointerAdrress(data): Return the address of a pointer
	"""

	pointer1 = int(ord(data[0])) & 0b00111111
	pointer2 = int(ord(data[1])) & 0b11111111

	retval = (256 * pointer1) + pointer2

	return(retval)


def extractDomainName(index, data, debug_bad_pointer = False):
	"""
	extractDomainName(answer, data) - Extract a domain-name as defined in RFC 1035 3.3
	
	In more detail, this function takes a string which consists of 1 or more bytes
	which indicate length, followed by a string.  It is terminated by a byte
	of value 0x00.
	
	Sanity checking is done if either of the first two bits of the pointer is set--if just
	one bit or the other is set, that is logged.

	Return values:
		- A string
		- An array of sanity checks that failed for this answer
		- and metadata on this answer, such as pointer traversal
	"""

	retval = ""
	sanity = []
	meta = {}
	meta["index_start"] = index
	meta["pointers"] = []

	beenhere = {}
	#beenhere[21] = True # Debugging

	while True:

		length = int(ord(data[index]))
		if debug_bad_pointer:
			length = 0b01000000 # Debugging

		if length == 0:
			break

		elif length & 0b11000000:

			#
			# Make sure both of the first bits are set
			#
			if length != 192:
				sanity.append("Bad pointer! Expected value of 192, got %d!" % length)
				break

			pointer = getPointerAddress(data[index:index + 2])
			logger.debug("Pointer found!  Raw value: %s, interpreted value: %d" % (
				formatHex(data[index:index + 2]), pointer))

			if pointer in beenhere:
				logger.warn("extractDomainName(): We were previously at this pointer, bailing out! "
					+ "pointer=%s, beenhere=%s" % (pointer, beenhere))
				sanity.append("Previously at pointer %s, bailing out! (Beenhere: %s)" % (pointer, beenhere))
				break

			beenhere[pointer] = True

			length = int(ord(data[pointer]))
			index = pointer

		else:
			#
			# Just a length, so set our pointer to zero.
			#
			pointer = 0

		#
		# Chop off the first byte and get our domain-name
		#
		domain_name = data[index + 1:]
		string = domain_name[0:length]

		#
		# If we have a pointer in this iteration, store it and what it points to in our metadata.
		#
		if pointer:
			pointer_data = {
				"pointer": pointer,
				"target": string,
				}
			meta["pointers"].append(pointer_data)

		if retval:
			retval += "."
		retval += string

		index += 1 + length

	return(retval, sanity, meta)


def parseAnswerHeaders(data):
	"""
	parseAnswerHeaders(data): Parse the headers out of our answer
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

	retval["type"] = (256 * ord(data[2])) + ord(data[3])
	retval["class"] = (256 * ord(data[4])) + ord(data[5])

	retval["type_text"] = parseQtype(retval["type"])
	retval["class_text"] = parseQclass(retval["class"])

	retval["ttl"] = (256 * ord(data[8])) + ord(data[9])
	retval["rdlength"] = (256 * ord(data[10])) + ord(data[11])

	return(retval)


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

	text = formatHex(answer, delimiter = ":", group_size = 4)

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
	(text, retval["sanity"], retval["meta"]) = extractDomainName(index, data)

	return(retval, text)

def parseAnswerCname(answer, index, data):
	"""
	parseAnswerCname(answer, data): Parse a Cname answer.
	
	answer - The answer body (no headers)
	data - The entire response packet
	
	"""

	retval = {}

	index += 12
	(text, retval["sanity"], retval["meta"]) = extractDomainName(index, data)

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
	(exchange, retval["sanity"], retval["meta"]) = extractDomainName(index, data)

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

	(mname, retval["sanity"], _) = extractDomainName(index, data)
	index += len(mname) + 2

	#
	# Pull out the domain-name of the mailbox of the person resonsible.
	#
	(rname, offset, _) = extractDomainName(index, data)
	index += len(rname) + 2

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


	return(retval, retval_text)


def parseAnswers(data, question_length = 0):
	"""
	parseAnswers(data): Parse all answers given to a query
	"""

	retval = []

	index = 12 + question_length
	logger.debug("question_length=%d total_length=%d" % (question_length, len(data)))

	while True:

		answer = {}
		logger.debug("parseAnswers(): Index is currently %d" % index)
	
		answer["headers"] = parseAnswerHeaders(data[index:])

		#
		# Advance our index to the start of the next answer, then put this entire
		# answer into answer["rddata_raw"]
		#
		index_old = index
		index_next = index + 12 + answer["headers"]["rdlength"]
		answer["rddata_raw"] = data[index:index_next]

		(answer["rddata"], answer["rddata_text"]) = parseAnswerBody(answer, index, data)
		index = index_next

		#
		# This is a bit of hack, but we want to grab the sanity data from the rddata 
		# dictonary and put it into its own dictionary member so that the sanity
		# module can later extract it.
		#
		answer["sanity"] = {}
		if "sanity" in answer:
			answer["sanity"] = answer["rddata"]["sanity"]
			del answer["rddata"]["sanity"]

		#
		# Deleting the raw data because it will choke when convered to JSON
		#
		answer["rddata_hex"] = {}
		if "rddata_hex" in answer:
			answer["rddata_hex"] = formatHex(answer["rddata_raw"])
			del answer["rddata_raw"]

		retval.append(answer)

		#
		# If we've run off the end of the packet, then break out of this loop
		#
		if index >= len(data):
			logger.debug("parseAnswer(): index %d >= data length (%d), stopping loop!" % (index, len(data)))
			break

	return(retval)
	

