#!/bin/bash
# 
# This script runs tests again our DNS tool, but does so on an automated bassis.
#

# Errors are fatal
set -e

#set -x # Debugging

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
	"11e42c921b732897b569b4c0dee9991c4efa505f"
	"e33cee2fe96f2fbdf10d5a6b31f43237e95b3c89"
	"98ce146d5526b944bd62b48e3054f4fc513dfcac"
	"4f649dfa2fb229ccb83b3ad85862838101a8f9bb"
	"df558239d4bad199a98c8aecaa280b86a070b245"
	"83838e0438bce7482b6656661fd910e7e8287d1f"
	)
declare -a ANSWERS_TEXT_HASH=(
	"53d5b09c49c45416ef1ac7336a1d9d2a709c094b"
	"4418db88ce962b338ad1a398d1c2ed189b11b889"
	"8af3a50bdbb4e8e3d1a006497e5aa61d2db599dd"
	"b352fa4e5639ea4a95409928479d91c82677ff2a"
	"b163f667583713528b4df289048608783fae0e09"
	"1d8be7b64cd979b3b27ee713fd14b3e97f2f35f6"
	)
declare -a ANSWERS_GRAPH_HASH=(
	"fe538a5673df8793e35cad16c0e3b65c34afd0ba"
	"76a48768d38d5000b5dc55735c9f0861e116655d"
	"31540cd538aaefd9c63673276ccb150acb212832"
	"173fd95f6c87664f86b06892edd6083e87aa937d"
	"75b4522bd83ecff88c611c11d56892221d07a101"
	"48e8a4e10552145fc87482d291477da4b7e543f6"
	)
declare -a ANSWERS_RAW_STDIN_HASH=(
	"39b053f57dc266ada1628d86f3db1f90e1cefb56"
	"0e4e899eaaddca85cc01dc058b90652f6c21b011"
	"b41749af296f82bdc51ddf417a4e7061589dd491"
	"ac18326927085c1d7779024e568b3e7ca048c0a5"
	"2089267cd27f4f19679542a048d1dcd23db4a0bf"
	"d6e73fd52201907c9ee5b1e8a712d6112a21cd4e"
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
		#exit 1 # Debugging

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


#
# I have no idea if this value will change, so I'm doing this here, and checking plaintext 
# instead of messing with hashes.
#
RESULT=$(./dns-tool.py -q --fake-ttl --request-id 0000 --json testing.invalid | jq -r .answers[].rddata_text)
EXPECTED="a.root-servers.net nstld.verisign-grs.com 2018041701 1800 900 604800 86400"
test_result "bad-tld" "$RESULT" "$EXPECTED"




