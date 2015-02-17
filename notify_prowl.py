#!/usr/bin/env python
# -*- coding: utf-8 -*-

# regular python modules needed for this project
import sys, syslog, email, re, argparse

# this project relies on prowlpy which is saved in the same folder as the script
# https://github.com/jacobb/prowlpy
import prowlpy

# next we import the decode_header function from email.header
# if you don't do this utf-8 encoded "from" and "subject" fields won't appear properly
from email.header import decode_header

program_description = 'Reads an email message from the standard input and uses it to send a new mail notification via prowlapp. '
program_description = program_description + 'To use this program you must have installed and activated the prowl application on your device first. '
program_description = program_description + 'To get your apikey, see https://www.prowlapp.com/api_settings.php while logged-in to your own account.'

# define the command line arguments
parser = argparse.ArgumentParser(description=program_description)
parser.add_argument('-apikey', required=True, help='your personal apikey from your prowlapp.com account (required)')
parser.add_argument('-priority', type=int, default=0, choices=range(-2,3), help='which Prowl priority to use for the message (default: -1)')
parser.add_argument('-application', default='Mail', help='the appliation name to supply to Prowl for long format (default: Mail)')
parser.add_argument('-format', default='short', choices=['short', 'long'], help='specifies which format to send to Prowl (default: short)')
parser.add_argument('-addfrom', default=False, action='store_true', help='append the word "from" before the sender when using the long format (if not specified then False)')
args = parser.parse_args()

# initialize an exit code to use later
# if we don't run into any errors 0 means everything's OK
exit_code = 0

# this script reads the whole email from the standard input
# it was originally used with a dovecot pigeonhole sieve "pipe" script
full_msg = sys.stdin.readlines()
msg = email.message_from_string(''.join(full_msg))

# now read the raw from and subject fields
the_from = msg['from']
the_subject = msg['subject']

# to process them, first decode the subject and headers
the_subject = decode_header(the_subject)
subject_encoding = [subject[1] for subject in the_subject][0]
the_subject = [subject[0] for subject in the_subject][0]
the_from = decode_header(the_from)
from_encoding = [afrom[1] for afrom in the_from][0]
the_from = [afrom[0] for afrom in the_from][0]

# if there was no encoding, the result is the None object
# in this case, we need a string to indicate none
if subject_encoding is None:
    subject_encoding = 'none'
if from_encoding is None:
    from_encoding = 'none'

# next, extract the name out of the most commone email address format
match = re.search('(.*) <.*@.*>', the_from)
if match:
    the_from = match.group(1)

# next, extract the name out of another common format for email address
match = re.search('.*@.* \((.*)\)', the_from)
if match:
    the_from = match.group(1)

# next, extract any parenthesis, quotation marks, or angle brackets from the ends
# not often necessary, but email address formats aren't standard
# and we want this to look as pretty as possible
the_from = the_from.strip(' "()<>')

# remove any spaces from the beginning or end of the subject
the_subject = the_subject.strip()

original_from = the_from
original_subject = the_subject

# next, truncate the fields to the maximum amount allowed by the prowlapp api
if (args.format == 'short'):
	the_from = the_from[:256]
	the_subject = the_subject[:1024]
else:
	if args.addfrom:
		the_from = 'from ' + the_from
	args.application = args.application[:256]
	the_from = the_from[:1024]
	the_subject = the_subject[:10000]

# log what's happening to the mail system log
syslog.openlog(ident='notify_prowl', facility=syslog.LOG_MAIL, logoption=syslog.LOG_PID)
syslog.syslog(' '.join(sys.argv) + ' | ' + original_from + ' | ' + original_subject + ' (from/subject encoding '  + from_encoding + '/' + subject_encoding + ')')

# open the connection to prowl
p = prowlpy.Prowl(args.apikey)
try:
    # try to send our message. if we don't have an exception, we were successful
    if (args.format == 'short'):
    	p.add(application = the_from, event = the_subject, description = '', priority = args.priority)
    else:
	p.add(application = args.application, event = the_from, description = the_subject, priority = args.priority)
    syslog.syslog('Prowl Message Sent');
except Exception,msg:
    # if there was any exception, log it and get ready to send an error
    syslog.syslog(msg[0])
    exit_code = 1;

# close the logging system
syslog.closelog()

# let the calling program know how we did
sys.exit(exit_code)
