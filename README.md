
# DNS TOOL

This is a DNS tool I wrote, based off [an example I found here](https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html).

It is a work in progress, and will be updated.


## Features

- Output in text, JSON, and pretty-printed JSON
- Debugging support with Python's builtin logger app
- Sanity Checking module which reports on any inconsistencies it finds in the response.


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


## Module Architecture

- create.py: Functions for creating the DNS request
- output.py: Functions for printing out the answer to a DNS query
- parse.py: Functions to parse the answer
- sanity.py: Functions to perform sanity checks on answer


## TODO List

- Random Request ID
- Parse SOA results
- Argument for question type (CNAME, NS, etc.)
- How to handle multiple answers? (NS, etc.)
- IPv6: Do queries for "AAAA" if "A" is specified.
- Handle RDNS queries/responses


## Further Reading

- https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html
- http://www.tcpipguide.com/free/t_DNSMessageHeaderandQuestionSectionFormat.htm
- https://tools.ietf.org/html/rfc1035


## Contact

If you see anything wrong, or anything you'd like add, feel free to open an issue.
You can also find me on [Twitter](http://twitter.com/dmuth) and [Facebook](http://www.facebook.com/dmuth).


