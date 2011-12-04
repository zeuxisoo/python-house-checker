# -*- coding: utf-8 -*-
import urllib2, re
import config

from google.appengine.api import mail

def fetch_current_data():
	html = urllib2.urlopen("http://www.housingauthority.gov.hk/tc/flat-application/allocation-status/index.html").read()

	# Highest Investigation and Allocation Number
	subject_pattern = re.compile(r'<p><strong>(?P<subject>.*?)\((?P<year_month>.*?)\)</strong></p>')
	subject_result = subject_pattern.search(html)

	year_month = subject_result.group('year_month')

	# 3-person Urban District
	found_out_result = re.compile(r'<td style="padding:5px 0px 5px 4px;">.*?</td>', re.MULTILINE).findall(html)[4]
	found_out_number = re.compile(r'<td style="padding:5px 0px 5px 4px;">(.*?)</td>').search(found_out_result).group(1)

	converted_number = ''.join(found_out_number.replace("&nbsp;", " ").split(" "))

	return {
		"year_month": year_month.decode("utf8"),
		"current_number": int(converted_number[1:])
	}

def send_mail(year_month, current_number, history, to, subject = "Public House Checker! Found new Current Number"):
	if len(history) <= 0 or history is None:
		history = "(empty)"

	message = mail.EmailMessage(
		sender = config.mail_sender,
		subject = subject,
	)
	message.to = to
	message.html ="""
<p>Well…</p>

The public house checker found new current number<br />
New number is <strong>%s</strong><br />
New year and month is <strong>%s</strong><br />

<p>History</p>

%s
""" % (current_number, year_month, history)
	message.send()