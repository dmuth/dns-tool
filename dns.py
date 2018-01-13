#!/usr/bin/env python
#
# A script to send messages to DNS servers and parse the responses.
# Based off of the example at https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
#


import argparse
import binascii
import json
import logging
import math
import socket


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# Parse our arguments.
#
parser = argparse.ArgumentParser(description = "Make DNS queries and tear apart the result packets")
parser.add_argument("--debug", "-d", action="store_true", help = "Enable debugging")
#parser.add_argument("bucket")
#parser.add_argument("file", nargs="?", help = "JSON file to write (default: output.json)", default = "output.json")
#parser.add_argument("--filter", help = "Filename text to filter on")

args = parser.parse_args()
logger.info("Args: %s" % args)

if args.debug:
	logger.setLevel(logging.DEBUG)


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


def sendUdpMessage(message, address, port):
	"""sendUdpMessage sends a message to UDP server

	message should be a hexadecimal encoded string
	"""
    
	retval = {}

	message = message.replace(" ", "").replace("\n", "")
	server_address = (address, port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		sock.sendto(binascii.unhexlify(message), server_address)
		data, _ = sock.recvfrom(4096)

		retval["header"] = parseHeader(data[0:12])
		retval["question"] = parseQuestion(data[12:])

		answer_index = 12 + retval["question"]["question_length"]
		retval["answer"] = parseAnswer(data[answer_index:])

		retval["raw"] = binascii.hexlify(data).decode("utf-8")

	finally:
		sock.close()

	return(retval)


def formatHex(hex):
	"""formatHex returns a pretty version of a hex string"""
	octets = [hex[i:i+2] for i in range(0, len(hex), 2)]
	pairs = [" ".join(octets[i:i+2]) for i in range(0, len(octets), 2)]
	return "\n".join(pairs)


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
		raise("Value %s is too large for a 16-bit int!" % val)

	return(retval)



def createHeader():
	"""createHeader(): Create a header for our question

	"""
	retval = ""

	# Request ID
	retval += chr(int("AA", 16))  + chr(int("AA", 16))


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


#
# TODO: 
#
# Build query with functions
#	createQuestion()
#
# Argument for question
# How to handle NXDOMAIN?
#
# Add more logging at info level :-)
#	Maybe something for when we're querying the server
#	Maybe something for what the query is...
#
# Argument for question type (CNAME, NS, etc.)
# How to handle multiple answers? (NS, etc.)
#
# Argument for DNS server
#
# Look up code as per http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
#

header = createHeader()
#print(formatHex(header))


message = "AA AA 01 00 00 01 00 00 00 00 00 00 " \
"07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"

response = sendUdpMessage(message, "8.8.8.8", 53)
#print(formatHex(response)) # Debugging
#print(response)
print(json.dumps(response, indent = 2))




