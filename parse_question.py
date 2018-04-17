

import logging
import struct

import output

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
	(retval["question"], _, retval["meta"]) = extractDomainName(index, data)
	index += len(retval["question"]) + 2

	#
	# Now pull out the QTYPE and QCLASS.
	#
	data = data[index:]

	retval["qtype"] = (256 * data[0]) + data[1]
	retval["qclass"] = (256 * data[2]) + data[3]
	data = data[4:]

	retval["qtype_text"] = parseQtype(retval["qtype"], question = True)
	retval["qclass_text"] = parseQclass(retval["qclass"])

	index += 4

	retval["question_length"] = index - index_start

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
	meta["pointers"] = []
	meta["data_decoded"] = []

	beenhere = {}
	#beenhere[21] = True # Debugging

	while True:

		length = data[index]
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
				output.formatHex(data[index:index + 2]), pointer))

			if pointer in beenhere:
				logger.warn("extractDomainName(): We were previously at this pointer, bailing out! "
					+ "pointer=%s, beenhere=%s" % (pointer, beenhere))
				sanity.append("Previously at pointer %s, bailing out! (Beenhere: %s)" % (pointer, beenhere))
				break

			beenhere[pointer] = True

			length = int(data[pointer])

			#
			# If this is our first pointer, make a note of what's two bytes after that, as 
			# in an SOA response, that will be the start of our headers.
			#
			if not "index_after_first_pointer" in meta:
				meta["index_after_first_pointer"] = index + 2

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
		string = domain_name[0:length].decode("utf-8")


		#
		# If we have a pointer in this iteration, store it and what it points to in our metadata.
		#
		if pointer:
			pointer_data = {
				"pointer": pointer,
				"target": string,
				}
			meta["pointers"].append(pointer_data)

			meta["data_decoded"].append({
				"pointer": pointer,
				"target": string,
				})

		else:
			#
			# If this is not a pointer and we haven't been to any pointers here,
			# copy the payload to our metadata.
			#
			if not len(meta["pointers"]):
				meta["data_decoded"].append({
					"length": length,
					"string": string,
					})

		if retval:
			retval += "."

		retval += string

		index += 1 + length

	meta["data_decoded"].append({
		"length": 0,
		})

	return(retval, sanity, meta)


def getPointerAddress(data):
	"""
	getPointerAdrress(data): Return the address of a pointer
	"""

	pointer1 = int(data[0]) & 0b00111111
	pointer2 = int(data[1]) & 0b11111111

	retval = (256 * pointer1) + pointer2

	return(retval)





