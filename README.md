<img src="./img/networking.svg" width="250" align="right" />

# DNS Tool

This is a DNS tool I wrote, based off [example code I found here](https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html).
It creates DNS packets from scratch and sends the queries to a DNS server.

It is a work in progress, and will be updated.


## Features

- Output in text, JSON, and pretty-printed JSON
- Debugging support with Python's builtin logger app
- Sanity Checking module which reports on any inconsistencies it finds in the response.


## Requirements

- Python 3
- A desire to learn more about how the Internet works


## Usage

```
usage: dns-tool.py [-h] [--debug] [--json] [--json-pretty-print] [--text]
                   query [server]

Make DNS queries and tear apart the result packets

positional arguments:
  query                String to query for (e.g. "google.com")
  server               DNS server (default: 8.8.8.8)

optional arguments:
  -h, --help           show this help message and exit
  --debug, -d          Enable debugging
  --json               Output response as JSON
  --json-pretty-print  Output response as JSON Pretty-printed
  --text               Output response as formatted text
```


## Sample Run

Let's run a query for google.com:

```
$ ./dns-tool.py google.com --text 
Question
========
   Question: google.com (len: 16)
   Type:     1 (A (Address))
   Class:    1 (IN)

Header
======
   Request ID:         aaaa
   Questions:          1
   Answers:            1
   Authority records:  0
   Additional records: 0
   QR:     Response
   AA:     Server isn't an authority
   RD:     Recursion requested
   RA:     Recursion available!
   OPCODE: Standard query
   RCODE:  No errors reported

Answer
======
   Answer:     172.217.5.238
   QCLASS:     1 (IN)
   QTYPE:      1 (A (Address))
   TTL:        93
   Raw RRDATA: acd905ee (len 4)
```


## Sanity Checking

This app also supports sanity checking on responses it gets from DNS servers.
If something is off (usage of a reserved field, etc.), the app will let you know.
Here is sample output from a run with `--text`:

```
Answer
======
   Answer:     172.217.15.110
   QCLASS:     123 (IN)
   QTYPE:      123 (A (Address))
   TTL:        216
   Raw RRDATA: acd90f6e (len 4)

Sanity Checks Failed
====================
   Content of Z field in header is not zero: 2
   Request ID on answer (aaaa) != request ID of question (beef)!
   OPCODE > 2 reserved for future use! (Qtype = 14)
   Invalid RCODE (77)
   QCLASS in answer is < 1 (0)
   QTYPE in answer is > 16 (123)
```


## Module Architecture

- `create.py`: Functions for creating the DNS request
- `output.py`: Functions for printing out the answer to a DNS query
- `parse.py`: Functions to parse the answer
- `sanity.py`: Functions to perform sanity checks on answer


## TODO List

- Random Request ID
- Argument for question type (CNAME, NS, etc.)
- How to handle multiple answers? (NS, etc.)
- IPv6: Do queries for "AAAA" if "A" is specified.
- Handle RDNS queries/responses
- Unit testing for parsing functions
- Functionality testing for queries against a DNS server
- Docker container to run a custom DNS server
- Docker containers to run different DNS servers and verify behavior across different DNS server software


## Further Reading

- https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
- http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
- https://tools.ietf.org/html/rfc1035


## Credits

- Icon made by <a href="https://www.flaticon.com/authors/gregor-cresnar" title="Gregor Cresnar">Gregor Cresnar</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a>.


## Contact

If you see anything wrong, or anything you'd like add, feel free to open an issue.
You can also find me on [Twitter](http://twitter.com/dmuth) and [Facebook](http://www.facebook.com/dmuth).


