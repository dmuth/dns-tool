

import datetime
import logging
import struct

import humanize

import output
import parse_answer_body
import parse_question


logger = logging.getLogger()


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
	# 6-9: TTL
	# 10-11: RDLENGTH
	# 12+: RDDATA (The answer!)
	#

	retval["type"] = (256 * ord(data[2])) + ord(data[3])
	retval["class"] = (256 * ord(data[4])) + ord(data[5])

	retval["type_text"] = parse_question.parseQtype(retval["type"])
	retval["class_text"] = parse_question.parseQclass(retval["class"])

	#data = data[0:6] + "0" + data[7:] # Debugging - Make the TTL 25+ years
	retval["ttl"] = ( ( 16777216 * ord(data[6]) ) + ( 65536 * ord(data[7]) ) + ( 256 * ord(data[8])) ) + ord(data[9])
	retval["ttl_text"] = humanize.naturaltime(datetime.datetime.now() + datetime.timedelta(seconds = retval["ttl"]))
	retval["rdlength"] = (256 * ord(data[10])) + ord(data[11])

	return(retval)


def parseAnswers(data, question_length = 0):
	"""
	parseAnswers(data): Parse all answers given to a query
	"""

	retval = []

	#
	# Skip the headers and question
	#
	index = 12 + question_length
	logger.debug("question_length=%d total_length=%d" % (question_length, len(data)))

	if index >= len(data):
		logger.debug("parseAnswer(): index %d >= data length(%d), so no answers were received. Aborting." % (
			index, len(data)))
		return(retval)

	#
	# Now loop through our answers.
	#
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
	


