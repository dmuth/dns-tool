

import datetime
import logging
import struct

import humanize

import output
import parse_answer_body
import parse_question


logger = logging.getLogger()


def parseAnswerHeaders(args, data):
	"""
	parseAnswerHeaders(args, data): Parse the headers out of our answer
	"""

	retval = {}

	#
	# RR bytes:
	#
	# 0-1: Bits 2-15 contain the offset to the question that this answer answers.
	# 2-3: Type
	# 4-5: Class
	# 6-9: TTL
	# 10-11: RDLENGTH
	# 12+: RDDATA (The answer!)
	#

	#
	# Set our offsets for the different parts of the Answer Header.
	#
	offset_type = 2
	offset_class = 4
	offset_ttl = 6
	offset_rdlength = 10

	#
	# This is going to be the angriest comment of my entire career.
	# Remember the part above where I saw the first two bytes are the offset
	# to the question?  Well, if you do a specific type of query--a query against
	# a non-existent TLD, you can forget what I just said.  In the case of a
	# non-existant TLD such as "testing.bad", you won't get back a pointer to the question, nope!
	# Instead what you'll get is a single byte which has the value of zero. Awesome!
	#
	# I don't know if it was mentioned somewhere in RFC 1035 and I just missed it,
	# or if the behavior of DNS changed in a later RFC.  Either wya, this bug vexed me
	# for WEEKS until I started going through actualy hex dumps and tracked it down.
	# 
	# /rant
	#
	if data[0] == 0:
		offset_type -= 1
		offset_class -= 1
		offset_ttl -= 1
		offset_rdlength -= 1

	retval["type"] = (256 * data[offset_type]) + data[offset_type + 1]
	retval["class"] = (256 * data[offset_class]) + data[offset_class + 1]

	retval["type_text"] = parse_question.parseQtype(retval["type"])
	retval["class_text"] = parse_question.parseQclass(retval["class"])

	#data = data[0:6] + struct.pack("B", 48) + data[7:] # Debugging - Make the TTL 25+ years
	if args.fake_ttl:
		logger.debug("parseAnswerHeaders(): --fake-ttl is set, setting TTL to -1")
		retval["ttl"] = -1

	else:
		retval["ttl"] = ( 16777216 * data[offset_ttl] ) + ( 65536 * data[offset_ttl + 1] ) + ( 256 * data[offset_ttl + 2] ) + data[offset_ttl + 3] 

	retval["ttl_text"] = humanize.naturaltime(datetime.datetime.now() + datetime.timedelta(seconds = retval["ttl"]))
	retval["rdlength"] = (256 * data[offset_rdlength]) + data[offset_rdlength + 1]

	return(retval)


def parseAnswersFakeTtl(args, data, question_length):
	"""
	parseAnswersFakeTtl(args, data, question_length): A clone of parseAnswers, but all this function does
		is set the TTL to 0xdeadbeef in answers and returned the altered message.  
		This is used when --fake-ttl is specified with --raw, and is useful for testing purposes.
	"""

	#
	# Skip the headers and question
	#
	index = 12 + question_length
	logger.debug("question_length=%d total_length=%d" % (question_length, len(data)))

	if index >= len(data):
		logger.debug("parseAnswer(): index %d >= data length(%d), so no answers were received. Aborting." % (
			index, len(data)))
		return(data)

	#
	# Now loop through our answers.
	#
	while True:

		answer = {}
		logger.debug("parseAnswersFakeTtl(): Index is currently %d" % index)
	
		#
		# If we're doing a fake TTL, we also have to fudge the response header and overwrite
		# the original TTL.  In this case, we're doing to overwrite it with -3 (4294967293).
		# That is a number (hopefully) unlikely to occur in nature.
		#
		ttl_index = index + 6
		logger.debug("parseAnswersFakeTtl(): --fake-ttl set, forcing TTL to be -3")
		data = data[0:ttl_index] + struct.pack(">i", -3) + data[ttl_index + 4:]

		#
		# Advance our index to the start of the next answer
		#
		index_old = index
		answer["headers"] = parseAnswerHeaders(args, data[index:])
		index = index + 12 + answer["headers"]["rdlength"]

		#
		# If we've run off the end of the packet, then break out of this loop
		#
		if index >= len(data):
			logger.debug("parseAnswer(): index %d >= data length (%d), stopping loop!" % (index, len(data)))
			break

	return(data)


def parseAnswers(args, data, question_length = 0):
	"""
	parseAnswers(args, data): Parse all answers given to a query
	"""

	retval = []

	#
	# Skip the headers and question
	#
	index = 12 + question_length
	logger.debug("question_length=%d total_length=%d" % (question_length, len(data)))

	if index >= len(data):
		logger.debug("parseAnswers(): index %d >= data length(%d), so no answers were received. Aborting." % (
			index, len(data)))
		return(retval)

	#
	# Now loop through our answers.
	#
	while True:

		answer = {}
		logger.debug("parseAnswers(): Index is currently %d" % index)
	
		#
		# If we're doing a fake TTL, we also have to fudge the response header and overwrite
		# the original TTL.  In this case, we're doing to overwrite it with the 4 byte string
		# of 0xDEADBEEF, so that it will be obvious upon inspection that this string was human-made.
		#
		if args.fake_ttl:
			ttl_index = index + 6
			#
			# If the leading byte of the Answer Headers is zero (the question), then
			# the question was for a bad TLD, and the "pointer" is really just a single
			# byte, so go forward one byte less.
			#
			if data[index] == 0:
				ttl_index -= 1
			data_new = bytes()
			logger.debug("parseAnswers(): --fake-ttl specified, forcing TTL to be -2")
			data_new = data[0:ttl_index] + struct.pack(">i", -2) + data[ttl_index + 4:]
			data = data_new

		answer["headers"] = parseAnswerHeaders(args, data[index:])

		#
		# Advance our index to the start of the next answer, then put this entire
		# answer into answer["rddata_raw"]
		#
		index_old = index
		index_next = index + 12 + answer["headers"]["rdlength"]
		answer["rddata_raw"] = data[index:index_next]

		(answer["rddata"], answer["rddata_text"]) = parse_answer_body.parseAnswerBody(answer, index, data)
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
			answer["rddata_hex"] = output.formatHex(answer["rddata_raw"])
			del answer["rddata_raw"]

		retval.append(answer)

		#
		# If we've run off the end of the packet, then break out of this loop
		#
		if index >= len(data):
			logger.debug("parseAnswer(): index %d >= data length (%d), stopping loop!" % (index, len(data)))
			break

	return(retval)
	


