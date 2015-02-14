# notify_prowl
reads an email from the standard input and uses prowlpy to send a notification to prowl

Written by Jedediah C. Daiger, (c) 2015

Dependencies
------------
In order to use this system, you must use the prowl app for sending notifications to your mobile device. See http://prowlapp.com for more information.

This script depends on the prowlpy module in order to connect to the notification service. See https://github.com/jacobb/prowlpy/ for more inforamtion. You may either install this script into your Python installation or simply let it reside in the same folder as notify_prowl.

Installation
------------
Where and how you install this script will depend on how you use it. For one example of how I used it with the dovecot mail server's sieve script functionality, see DOVECOT_EXAMPLE.txt.

How to Use
----------
You'll get the most use of this script when plugging it into an MTA or MDA process. It will read the standard input for an entire email message, including headers, and process that message to create a Prowl notification. For now, that notification will set the sender of the email as the "application" and the subject of the email as the "event." The rest of the email is not used- or processed-by this script.

The easiest way to use this script is to pass it an email message through the pipe. Every single time you use the program you must pass your Prowll apikey. To find your apikey, see https://www.prowlapp.com/api_settings.php while logged-in to your own account. Example:
     cat test.msg | notify_prowl.py -apikey dh374djwg7dh3udi2684kshuigh374l4m6jk3g5j

For a more specific example of how I used it with the dovecot mail server's seive script functionality, see DOVECOT_EXAMPLE.txt.

Change Log
----------
v 1.0
     - initial release

To-Do
-----
	* additional runtime configuration options for the actual content of the notification
