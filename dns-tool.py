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

import parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#
# Parse our arguments.
#
parser = argparse.ArgumentParser(description = "Make DNS queries and tear apart the result packets")
parser.add_argument("--debug", "-d", action = "store_true", help = "Enable debugging")
parser.add_argument("--json", action = "store_true", help = "Output response as JSON")
parser.add_argument("--json-pretty-print", action = "store_true", help = "Output response as JSON Pretty-printed")
parser.add_argument("--text", action = "store_true", help = "Output response as formatted text")
parser.add_argument("query", help = "String to query for (e.g. \"google.com\")")
parser.add_argument("server", nargs = "?", default = "8.8.8.8", help = "DNS server (default: 8.8.8.8)")
#parser.add_argument("file", nargs="?", help = "JSON file to write (default: output.json)", default = "output.json")
#parser.add_argument("--filter", help = "Filename text to filter on")

args = parser.parse_args()
logger.info("Args: %s" % args)

if args.debug:
	logger.setLevel(logging.DEBUG)


def sendUdpMessage(message, address, port):
	"""sendUdpMessage(message, address, port): sends a message to UDP server

	message can be a raw string
	"""
    
	retval = {}

	server_address = (address, port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#
	# Set our timeout
	#
	sock.settimeout(3)

	try:
		logger.info("Sending query to %s:%s..." % (address, port))
		sock.sendto(message, server_address)
		data, _ = sock.recvfrom(4096)

		retval["header"] = parse.parseHeader(data[0:12])
		retval["question"] = parse.parseQuestion(data[12:])

		answer_index = 12 + retval["question"]["question_length"]
		retval["answer"] = parse.parseAnswer(data[answer_index:])

		retval["raw"] = binascii.hexlify(data).decode("utf-8")

	except socket.error as e:
		logger.error("Error connecting to %s:%s: %s" % (address, port, e))
		raise e

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
		raise Exception("Value %s is too large for a 16-bit int!" % val)

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


def createQuestion(q):
	"""createQuestion(q): Create the question part of our query

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

	# QTYPE - 1 is an A query
	qtype = 1
	retval += convertTo16Bit(qtype)

	# QCLASS - 1 is IN
	qclass = 1
	retval += convertTo16Bit(qclass)

	return(retval)


def printResponse(response):
	"""
	printResponse(response): Print up our response in 1 or more formats.
	"""

	#print(formatHex(response)) # Debugging
	#print(response)
	if args.json:
		print(json.dumps(response))

	if args.json_pretty_print:
		print(json.dumps(response, indent = 2))

	if args.text:
		printResponseText(response)


def printResponseText(response):
	"""
	printResponseText(response): Print up our response as text.
	"""

	question = response["question"]
	print("Question")
	print("========")
	print("   Question: %s (len: %s)" % (question["question"], question["question_length"]))
	print("   Type:     %d (%s)" % (question["qtype"], question["qtype_text"]))
	print("   Class:    %d (%s)" % (question["qclass"], question["qclass_text"]))

	print("")

	header = response["header"]
	text = header["header_text"]
	print("Header")
	print("======")
	print("   Request ID:         %s" % header["request_id"])
	print("   Questions:          %d" % int(header["num_questions"]))
	print("   Answers:            %d" % int(header["num_answers"]))
	print("   Authority records:  %d" % (int(header["num_authority_records"])))
	print("   Additional records: %d" % (int(header["num_additional_records"])))
    	print("   QR:    %s" % text["qr"])
	print("   AA:    %s" % text["aa"])
	print("   RD:    %s" % text["rd"])
	print("   RA:    %s" % text["ra"])
	print("   RCODE: %s" % text["rcode"])

	print("")

	answer = response["answer"]
	print("Answer")
	print("======")
	print("   Answer: %s" % answer["rddata_text"])
	print("   QCLASS: %s (%s)" % (answer["qclass"], answer["qclass_text"]))
	print("   QTYPE: %s (%s)" % (answer["qtype"], answer["qtype_text"]))
	print("   TTL: %s" % (answer["ttl"]))
	print("   Raw RRDATA: %s (len %s)" % (answer["rddata"], answer["rdlength"]))

	print("")



#
# TODO: 
#
# Argument for question type (CNAME, NS, etc.)
# How to handle multiple answers? (NS, etc.)
#
# Sanity
#	- Make sure request ID matches
#	- Make sure reserved fields are empty
#	- Make sure codes are what they should be
#
# Look up code as per http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
# 	https://tools.ietf.org/html/rfc1035#page-26
# 
# IPv6: Do queries for "AAAA" if "A" is specified. Handle things like rDNS?
#

header = createHeader()
logger.debug(parse.parseHeader(header))

question = createQuestion(args.query)
logger.debug(parse.parseQuestion(question))

message = header + question

response = sendUdpMessage(message, args.server, 53)

printResponse(response)





