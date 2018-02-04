#
# This module holds our code for printing out our responses.
#


import binascii
import json
import logging


logger = logging.getLogger()


def printResponse(args, response):
	"""
	printResponse(args, response): Print up our response in 1 or more formats.
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

	sanity = response["sanity"]

	question = response["question"]
	print("Question")
	print("========")
	print("   Question: %s (len: %s)" % (question["question"], question["question_length"]))
	print("   Type:     %d (%s)" % (question["qtype"], question["qtype_text"]))
	print("   Class:    %d (%s)" % (question["qclass"], question["qclass_text"]))
	print("   Server:   %s:%s" % (response["server"][0], response["server"][1]))
	
	print("")

	printHeader(response["header"], sanity["header"])

	print("")

	printAnswers(response["answers"], sanity["answers"])

	print("")


def printHeader(header, sanity):
	"""
	printHeader(header): Print up our headers
	"""

	text = header["header_text"]
	print("Header")
	print("======")
	print("   Request ID:         %s" % header["request_id"])
	print("   Questions:          %d" % int(header["num_questions"]))
	print("   Answers:            %d" % int(header["num_answers"]))
	print("   Authority records:  %d" % (int(header["num_authority_records"])))
	print("   Additional records: %d" % (int(header["num_additional_records"])))
	print("   QR:      %s" % text["qr"])
	print("   AA:      %s" % text["aa"])
	print("   TC:      %s" % text["tc"])
	print("   RD:      %s" % text["rd"])
	print("   RA:      %s" % text["ra"])
	print("   OPCODE:  %d - %s" % (header["header"]["opcode"], text["opcode_text"]))
	print("   RCODE:   %d - %s" % (header["header"]["rcode"], text["rcode_text"]))

	if len(sanity):
		for warning in sanity:
			print("   WARNING: %s" % warning)


def printAnswers(answers, sanity):

	print("Answers")
	print("=======")

	index = 0
	for answer in answers:

		headers = answer["headers"]
		meta = {}
		if "meta" in answer["rddata"]:
			meta = answer["rddata"]["meta"]

		print("   Answer #%d:   %s" % (index, answer["rddata_text"]))
		print("   CLASS:       %s (%s)" % (headers["class"], headers["class_text"]))
		print("   TYPE:        %s (%s)" % (headers["type"], headers["type_text"]))
		print("   TTL:         %s" % (headers["ttl"]))

		if "pointers" in meta and len(meta["pointers"]):
			print("   Pointers:")
			for pointer in meta["pointers"]:
				print("      Pointer to offset %d, points to '%s'" % (pointer["pointer"], pointer["target"]))

		print("   Raw RRDATA:  %s (len %s)" % (answer["rddata_hex"], headers["rdlength"]))
		print("   Full RRDATA: %s" % (answer["rddata"]))

		sanity_answer = sanity[index]
		if len(sanity_answer):
			for warning in sanity_answer:
				print("   WARNING:     %s" % warning)

		index += 1
		print("")


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



