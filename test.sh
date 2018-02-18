#!/bin/bash
# 
# This script runs tests again our DNS tool, but does so on an automated bassis.
#

# Errors are fatal
set -e


#
# Our query types to run
#
declare -a QUERY_TYPES=("a" "aaaa" "mx" "soa" "cname" "ns")

#
# The answers we are expecting.
#
declare -a ANSWERS=(
	"127.0.0.100"
	"fe80:0000:0000:0000:0000:0000:0000:0001"
	"10 test.dmuth.org"
	"ns-765.awsdns-31.net awsdns-hostmaster.amazon.com 1 7200 900 1209600 86400"
	"a.test.dmuth.org"
	#"BADns.test.dmuth.org" # Debugging
	"ns.test.dmuth.org"
	)
declare -a ANSWERS_MULTI=(
	"127.0.0.101 127.0.0.102 "
	"fe80:0000:0000:0000:0000:0000:0000:0002 fe80:0000:0000:0000:0000:0000:0000:0003 "
	"20 test2.dmuth.org 30 test3.dmuth.org "
	"ns-765.awsdns-31.net awsdns-hostmaster.amazon.com 1 7200 900 1209600 86400 "
	"ns-765.awsdns-31.net awsdns-hostmaster.amazon.com 1 7200 900 1209600 86400 "
	"ns.test.dmuth.org ns2.test.dmuth.org "
	)
declare -a ANSWERS_JSON_HASH=(
	"b815f1d664a28c7de2614f6e190ab6266f1d9c85"
	"468131187f09eca3bb483da4a9bb39bd54d69f9e"
	"7005acb3a1fc00b5e8b5a792d2671a5b70e534d7"
	"da6f152dfcbb167fb6891662fcf1388354eb1da3"
	"2d189dc5673c66be3cbe9858cf3a802132367e39"
	"d0585abb363dd950fc80a902f8df1a7d49d3b013"
	)
declare -a ANSWERS_TEXT_HASH=(
	"aa4b9c40f0fc60df9f817f37832b8987c6239e78"
	"06a9ab41af09b70a1f7d2ecf164484cf59d49b80"
	"9eb4bc2656730179b0a6c559864ca6fd58056725"
	"f837f86eb2ca051dc6632b1d53a58ca7974c080e"
	"66b8ff201b54e686abb8be750f811ce6b52dcb32"
	"7de2f450ec22e6ac7e65901c0d36aa6b591276c7"
	)
declare -a ANSWERS_GRAPH_HASH=(
	"d2aa805a48b598a9bffc6f135388ef75a4a65a4b"
	"a637b4dc17cc65cf57603efe5392bbe93112903d"
	"83c4388d211e112670e4cea44f519cb329cd5326"
	"1cfdb054d5e20ee88e62708eae27cd4a01316c6e"
	"2a3af746e8c67a91ea0eb3ae043ea93f70488f92"
	"8f9bee3cab0c7654eeda704d6f92a2a64d17d1af"
	)
declare -a ANSWERS_RAW_STDIN_HASH=(
	"e46731d9fcc7079a8cd5a3ee3b6a0b9c2e33e290"
	"251f7192008dd437ec2f961009e2e98b09558054"
	"162f329ab3c9983b959a17d578668e540f62bb81"
	"03a325684847bd592c06f892b1b37909bc74f45b"
	"fb326eedd537fe3c260eaff77064166fe47d18bc"
	"691487d60cdd31c7222633b849be391f984c968b"
	)

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'


#
# Check our results against what was expected.
#
function test_result() {

	local QUERY=$1
	local RESULT=$2
	local EXPECTED=$3

	if test "$RESULT" == "$EXPECTED"
	then
		echo -e "   ${GREEN}[OK]${NC}    : result '${RESULT}' checks out for query '${QUERY}'"

	else
		echo -e "   ${RED}[ERROR]${NC} : result '${RESULT}' != '${EXPECTED}' for query '${QUERY}'"
		# TEST
		#exit 1

	fi

} # End of test_result()


#
# Loop through our query types, run a query for each test record, 
# and compare the results!
#
INDEX=0
for TYPE in ${QUERY_TYPES[@]}
do

	DNS_SERVER=""

	if test "$TYPE" == "ns"
	then
		DNS_SERVER="ns-49.awsdns-06.com"
	fi

	QUERY="${TYPE}.test.dmuth.org"
	QUERY2="${TYPE}2.test.dmuth.org"

	EXPECTED="${ANSWERS[$INDEX]}"
	EXPECTED_MULTI="${ANSWERS_MULTI[$INDEX]}"
	EXPECTED_JSON_HASH="${ANSWERS_JSON_HASH[$INDEX]}"
	EXPECTED_TEXT_HASH="${ANSWERS_TEXT_HASH[$INDEX]}"
	EXPECTED_GRAPH_HASH="${ANSWERS_GRAPH_HASH[$INDEX]}"
	EXPECTED_RAW_STDIN_HASH="${ANSWERS_RAW_STDIN_HASH[$INDEX]}"

	ARGS="-q --request-id 1 --fake-ttl"

	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} --json ${QUERY} ${DNS_SERVER} | jq -r .answers[].rddata_text)
	test_result "$QUERY" "$RESULT" "$EXPECTED"

	#
	# Test against records that return multiple results.
	# Output is sorted and newlines are removed so that answers always the same oneliner.
	#
	# We can't do this for json, text, and graph because the order is not guaranteed.
	# (Maybe I can add an option for sorting in the future)
	#
	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} --json ${QUERY2} ${DNS_SERVER} | jq -r .answers[].rddata_text |sort |tr "\n" " ")
	test_result "$QUERY" "$RESULT" "$EXPECTED_MULTI"


	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} ${QUERY} ${DNS_SERVER} --json \
		| sha1sum | awk '{print $1}')
	test_result "$QUERY --json" "$RESULT" "$EXPECTED_JSON_HASH"


	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} ${QUERY} ${DNS_SERVER} --text \
		| sha1sum | awk '{print $1}')
	test_result "$QUERY --text" "$RESULT" "$EXPECTED_TEXT_HASH"


	RESULT=$(./dns-tool.py ${ARGS} --query-type ${TYPE} ${QUERY} ${DNS_SERVER} --graph \
		| sha1sum | awk '{print $1}')
	test_result "$QUERY --graph" "$RESULT" "$EXPECTED_GRAPH_HASH"


	CMD_OUT="./dns-tool.py ${ARGS} --query-type ${TYPE} --raw ${QUERY} ${DNS_SERVER}"
	CMD_IN="./dns-tool.py -q --text --stdin "
	#echo "$CMD_OUT | $CMD_IN" # Debugging
	RESULT=$($CMD_OUT | $CMD_IN | sha1sum | awk '{print $1}')
	test_result "$QUERY --raw | --stdin --text" "$RESULT" "$EXPECTED_RAW_STDIN_HASH"

	INDEX=$((INDEX += 1))

done




