#!/bin/bash
#
# A wrapper script to test our DNS tool
#



MULTIPLE=""
RECORD_TYPES=""


#
# Print our syntax and exit.
#
function printSyntax() {
	echo "! "
	echo "! Syntax: $0 --multiple [ record_type [ record_type [ ... ] ] ] "
	echo "! "
	echo "!		record_type - A, AAAA, MX, CNAME, SOA, TXT"
	echo "!		--mutiple - Specify if you want a DNS record returned with multiple responses"
	echo "! "
	exit 1

} # printSyntax()


#
# Parse our CLI arguments.
#
function parseArgs() {

	while test "$1"
	do
		ARG=$1

		if test "$ARG" == "--multiple"
		then
			MULTIPLE=2

		elif test "$ARG" == "a" -o "$ARG" == "A"
		then
			RECORD_TYPES="${RECORD_TYPES} a"

		elif test "$ARG" == "aaaa" -o "$ARG" == "AAAA"
		then
			RECORD_TYPES="${RECORD_TYPES} aaaa"

		elif test "$ARG" == "cname" -o "$ARG" == "CNAME"
		then
			RECORD_TYPES="${RECORD_TYPES} cname"

		elif test "$ARG" == "ns" -o "$ARG" == "NS"
		then
			RECORD_TYPES="${RECORD_TYPES} ns"

		elif test "$ARG" == "mx" -o "$ARG" == "MX"
		then
			RECORD_TYPES="${RECORD_TYPES} mx"

		elif test "$ARG" == "soa" -o "$ARG" == "SOA"
		then
			#
			# soa will be a non-existant record, which will result in an SOA response.
			#
			RECORD_TYPES="${RECORD_TYPES} soa"

		elif test "$ARG" == "txt" -o "$ARG" == "TXT"
		then
			RECORD_TYPES="${RECORD_TYPES} txt"

		else
			echo "$0: Unknown record type: '${ARG}'!"
			printSyntax

		fi

		shift

	done

	#
	# Didn't get any record types at all?  Bail!
	#
	if test ! "$RECORD_TYPES"
	then
		printSyntax
	fi

} # End of parseArgs()


#
# Parse our arguments
#
parseArgs $@


#
# Loop through our record types, generate the question for each, and make the query
#
for TYPE in $RECORD_TYPES
do

	QUESTION="${TYPE}${MULTIPLE}.test.dmuth.org"

	./dns-tool.py -q --query-type ${TYPE} --json ${QUESTION} #|jq .answers

done



