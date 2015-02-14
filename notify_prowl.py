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
parser.add_argument('-apikey', required=True, help='your personal apikey from your prowlapp.com account')
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

# next, truncate the from and subject fields to the maximum amount allowed by the prowlapp api
the_from = the_from[:256]
the_subject = the_subject[:1024]

# log what's happening to the mail system log
syslog.openlog(ident='notify_prowl', facility=syslog.LOG_MAIL, logoption=syslog.LOG_PID)
syslog.syslog(the_from + ' | ' + the_subject + ' (from/subject encoding ' + from_encoding + '/' + subject_encoding + ') (apikey=' + args.apikey + ')')

# open the connection to prowl
p = prowlpy.Prowl(args.apikey)
try:
    # try to send our message. if we don't have an exception, we were successful
    p.add(application = the_from, event = the_subject, description = '', priority = -1)
    syslog.syslog('Prowl Message Sent');
except Exception,msg:
    # if there was any exception, log it and get ready to send an error
    syslog.syslog(msg[0])
    exit_code = 1;

# close the logging system
syslog.closelog()

# let the calling program know how we did
sys.exit(exit_code)
