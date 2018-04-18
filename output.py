#
# This module holds our code for printing out our responses.
#


import binascii
import json
import logging


logger = logging.getLogger()

#
# Borrowed from https://docs.python.org/2/library/json.html
# This is used to print out object types when debugging where a bytes
# array is breaking JSON.dumps().
#
# To use it: 
#
#	json.dumps(data, cls = ComplexEncoder)
#
class ComplexEncoder(json.JSONEncoder):
	def default(self, obj):
		print("Object type", type(obj), obj)
		#return json.JSONEncoder.default(self, obj)

def printResponse(args, response):
	"""
	printResponse(args, response): Print up our response in 1 or more formats.
	"""

	if args.json:
		print(json.dumps(response))

	if args.json_pretty_print:
		print(json.dumps(response, indent = 2))

	if args.text or args.graph:
		printResponseText(args, response)


def printResponseText(args, response):
	"""
	printResponseText(response): Print up our response as text.
	"""

	if args.text or args.graph:

		sanity = response["sanity"]

		question = response["question"]

		printQuestion(args, question, response)
	
		print("")

		printHeader(args, response["header"], sanity["header"])
	
		print("")

		printAnswers(args, response["answers"], sanity["answers"])

		print("")


def printQuestion(args, question, response):
	"""
	printQuestion(args, question, response): Print our text and/or graph of our quesiton.
	"""

	print("Question")
	print("========")

	if args.text:
		print("")
		print("   Question: %s (len: %s)" % (question["question"], question["question_length"]))
		print("   Type:     %d (%s)" % (question["qtype"], question["qtype_text"]))
		print("   Class:    %d (%s)" % (question["qclass"], question["qclass_text"]))
		print("   Server:   %s" % (response["server"]))

	if args.graph:
		print("")
		print("                                1  1  1  1  1  1")
		print("     0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5")
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
		print("   |  QNAME: %-40s        |" % question["question"])
		for row in question["meta"]["data_decoded"]:
			length = row["length"]
			string = "(nil)"
			if length:
				string = row["string"]
			print("   |    len: %2d value: %-37s |" % (row["length"], string))

		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
		print("   |  QTYPE:  %3d - %-37s    |" % (question["qtype"], question["qtype_text"]))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
		print("   | QCLASS: %3d - %-38s    |" % (question["qclass"], question["qclass_text"]))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")


def printHeader(args, header, sanity):
	"""
	printHeader(header): Print up our headers
	"""

	text = header["header_text"]

	print("Header")
	print("======")

	if args.text:
		print("")
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

	#
	# Print a graph right out of RFC 1035, section 4.1.1
	#
	if args.graph:
		print("")
		print("                                1  1  1  1  1  1")
		print("     0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5")
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")
		print("   |             Request ID: %s                  |" % header["request_id"])
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")
		print("   |%s| Opcode: %d |%s|%s|%s|%s|  Z: %d  | RCODE: %d  |" % (
			"QR" if header["header"]["qr"] else "  ",
 			header["header"]["opcode"],
			"AA" if header["header"]["aa"] else "  ",
			"TC" if header["header"]["tc"] else "  ",
			"RD" if header["header"]["rd"] else "  ",
			"RA" if header["header"]["ra"] else "  ",
			header["header"]["z"],
			header["header"]["rcode"],
			))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")
		print("   |          Question Count: %d                    |" % int(header["num_questions"]))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")
		print("   |          Answer Count: %d                      |" % int(header["num_answers"]))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")
		print("   |          Authority/Nameserver Count: %d        |" % int(header["num_authority_records"]))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")
		print("   |          Additional Records Count: %d          |" % int(header["num_additional_records"]))
		print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+")


	if len(sanity):
		for warning in sanity:
			print("   WARNING: %s" % warning)


def printAnswers(args, answers, sanity):

	print("Answers")
	print("=======")

	index = 0
	for answer in answers:

		headers = answer["headers"]
		meta = {}
		if "meta" in answer["rddata"]:
			meta = answer["rddata"]["meta"]
		sanity_answer = sanity[index]

		if args.text:
			print("")
			printAnswerText(answer, index, headers, meta, sanity_answer)

		if args.graph:
			print("")
			printAnswerGraph(answer, headers, meta)

		index += 1


def printAnswerText(answer, index,  headers, meta, sanity_answer):
	"""
	printAnswerText(answer, index, headers, meta, sanity_answer): Print up text of our answer
	"""

	print("   Answer #%d:   %s" % (index, answer["rddata_text"]))
	print("   CLASS:       %s (%s)" % (headers["class"], headers["class_text"]))
	print("   TYPE:        %s (%s)" % (headers["type"], headers["type_text"]))
	print("   TTL:         %s (%s)" % (headers["ttl"], headers["ttl_text"]))

	if "pointers" in meta and len(meta["pointers"]):
		print("   Pointers:")
		for pointer in meta["pointers"]:
			print("      Pointer to offset %d, points to '%s'" % (pointer["pointer"], pointer["target"]))

	print("   Raw RRDATA:  %s (len %s)" % (answer["rddata_hex"], headers["rdlength"]))
	print("   Full RRDATA: %s" % (answer["rddata"]))

	if len(sanity_answer):
		for warning in sanity_answer:
			print("   WARNING:     %s" % warning)


def printAnswerGraph(answer, headers, meta):
	"""
	printAnswerGraph(answer, headers, meta): Print up a graph of our answer
	"""

	rddata = answer["rddata"]

	print("                                1  1  1  1  1  1")
	print("     0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5")
	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
    
	print("   |  NAME     : %-40s    |" % (rddata["question_text"]))

	for row in rddata["question_meta"]["data_decoded"]:

		if "length" in row:

			key = row["length"]
			value = "(nil)"
			if row["length"]:
				value = row["string"]
			print("   |        len: %3d  value: %-30s  |" % (key, value))

		elif "pointer" in row:
			key = row["pointer"]
			value = row["target"]
			print("   |    pointer: %3d target: %-30s  |" % (key, value))

		else:

			print("   |    UNKNOWN: %25s |" % (row))

	#
	# If the header was set to a negative very (or a very high positive value!)
	# for debugging, ensure the number is negative and the text indicates that
	# debugging is happening.
	#
	if headers["ttl"] >= 4294967293:
		logger.debug("TTL is over 2**32-3, so subtract 2**32")
		headers["ttl"] -= pow(2,32)

	if headers["ttl"] < 0:
		headers["ttl_text"] = "DEBUGGING"

	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
	print("   |  TYPE:  %3d - %-38s    |" % (headers["type"], headers["type_text"]))
	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
	print("   | CLASS: %3d - %-39s    |" % (headers["class"], headers["class_text"]))
	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
	print("   |   TTL: %10d - %-33s   |" % (headers["ttl"], headers["ttl_text"]))
	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
	print("   |   RDLENGTH: %3d                                         |" % (headers["rdlength"]))
	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")
	print("   |     RDDATA: %-40s    |" % (answer["rddata_text"]))
	if "meta" in rddata:
		for row in rddata["meta"]["data_decoded"]:

			if "length" in row:

				key = row["length"]
				value = "(nil)"
				if row["length"]:
					value = row["string"]
				print("   |        len: %3d  value: %-30s  |" % (key, value))

			elif "pointer" in row:
				key = row["pointer"]
				value = row["target"]
				print("   |    pointer: %3d target: %-30s  |" % (key, value))

			else:

				print("   |    UNKNOWN: %35s |" % (row))
	print("   +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+------------+")


def formatHex(data, delimiter = " ", group_size = 2):
	"""
	formatHex(data, delimiter = " ", group_size = 2): Returns a nice hex version of a string

	data - The string to turn into hex values
	delimiter - The delimter between hex values
	group_size - How many characters do we want in a group?
	"""

	if not isinstance(data, bytes):
		hex = bytearray(data, "iso8859-1").hex()
	else:
		hex = data.hex()
	
	retval = delimiter.join(hex[i:i + group_size] for i in range(0, len(hex), group_size))

	return(retval)



