#!/usr/bin/python
"""Convert CSV file to Python"""

import argparse
import csv
import pprint
import sys

TABS = [  # TODO: use enum?
    'FundList',
    'CelebrityList',
    'AssociateTable',
]

def Main():
  parser = argparse.ArgumentParser(description='Capture a picture from webcam.')
  parser.add_argument(
      '--input', help='The input CSV filename',
      type=argparse.FileType('r'),
      default=sys.stdin)
  parser.add_argument(
      '--output', help='The output Python filename',
      type=argparse.FileType('w'),
      default=sys.stdout)
  parser.add_argument(
      '--tab', type=str, choices=TABS,
      help='Specify the tab type')
  parser.add_argument('--loglevel', type=str, help='Loglevel')
  args = parser.parse_args()

  if args.loglevel:
    logging.basicConfig(level=getattr(logging, args.loglevel.upper()))

  if args.tab is None:
    # Use the input file name to guess
    if 'Fund List' in args.input.name:
      args.tab = 'FundList'
    elif 'Celebrity List' in args.input.name:
      args.tab = 'CelebrityList'
    elif 'Associate Table' in args.input.name:
      args.tab = 'AssociateTable'
    else:
      raise ValueError(
          'Cannot determine the input type. Please use --tab to specify')

  reader = csv.DictReader(args.input)

  # Check if key field is included.
  field_names = reader.fieldnames
  key_fields = [x for x in field_names if x == 'key' or x.startswith('key ')]
  if len(key_fields) > 1:
    raise ValueError(
        'Only one column starting with "key" is allowed. %p', key_fields)
  if len(key_fields) != 1:
    raise ValueError('the "key" field must be in the input. %p', field_names)
  # Remove 'key' field
  value_names = [x for x in field_names if x != key_fields[0]]

  output = {}
  for row in reader:
    key = row[key_fields[0]]
    if key in row:
      raise ValueError('Key (%s) is already existing', key)

    def StripCommentInParenthese(s):
      return s.split('(')[0].strip()

    output[key] = dict({
        StripCommentInParenthese(name): row[name] for name in value_names
    }, **{'key': key})

  args.output.write(
      '#!/usr/bin/python\n' +
      '\n' +
      'data = ')  # No newline
  pp = pprint.PrettyPrinter(indent=2, stream=args.output)
  pp.pprint(output)

if __name__ == "__main__":
  Main()
