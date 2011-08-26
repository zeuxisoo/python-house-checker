#/usr/bin/env python
# -*- coding: utf-8 -*-

# Load
import sys, os, datetime, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'library'))

import bottle
import helper, model, config

# Const variable
WWW_ROOT = os.path.abspath(os.path.dirname(__file__))

# Cron
@bottle.route('/cron')
def cron():
	logging.debug('Start cron')
	
	# Fetch page content
	current_data = helper.fetch_current_data()
	
	if current_data["year_month"] is not None and current_data["current_number"] is not None:
		logging.debug('Have year month and current number')
	
		# Initial house number model
		table = model.house_number()
		
		# Check current data is or not exists
		current_data_total = table.all().filter("subject = ", current_data["year_month"]).count()
		
		if current_data_total <= 0:
			# Insert new record
			table.subject = current_data["year_month"]
			table.current_number = current_data["current_number"]
			table.put()
			
			# Found out history
			history = []
			house_numbers = table.all().order("-create_at")
			for house_number in house_numbers:
				history.append(
					"<strong>%s</strong> at <strong>%s</strong><br />" % (
						house_number.subject, 
						house_number.current_number
					)
				)
			
			# Send mail
			helper.send_mail(
				year_month = current_data["year_month"].encode("utf8"),
				current_number = current_data["current_number"],
				history = (''.join(history)).encode("utf8"),
				to = config.mail_catcher
			)
			
			logging.info('Create new record success: %s, %s', current_data["year_month"].strip(), str(current_data["current_number"]))
		else:
			logging.warning('Create new record failed: not update content found in page')
		
		bottle.redirect('/')
	else:
		logging.error('current data may be None such as year_month and current_number field')
	
	logging.debug('End cron')

# Index
@bottle.route('/')
def index():
	return "Hello World"

# Create
@bottle.route('/create')
def create():
	current_data = helper.fetch_current_data()
	
	if current_data["year_month"] is not None and current_data["current_number"] is not None:
		table = model.house_number()
		
		# Check current data is or not exists
		current_data_total = table.all().filter("subject = ", current_data["year_month"]).count()
		
		if current_data_total <= 0:
			# Insert new record
			table.subject = current_data["year_month"]
			table.current_number = current_data["current_number"]
			table.put()
			
			bottle.redirect('/')
		else:
			return "Not create new record"
	else:
		bottle.redirect('/error/not-current-data')

# List
@bottle.route('/list')
def list():
	html = ['<p>show</p>']

	house_numbers = model.house_number.all().order("-create_at")
	for house_number in house_numbers:
		html.append(
			"<p>%s, %s, %s</p>" % (
				house_number.subject, 
				house_number.current_number, 
				(house_number.create_at + datetime.timedelta(hours=+8)).strftime("%Y-%m-%d %H:%M:%S %Z%z")
			)
		)

	html.append("total: %s" % str(model.house_number.all().count()) )

	return ''.join(html)

# Error
@bottle.route('/error/:code')
def error(code):
	return "<strong>Error!</strong> Got the <strong>%s</strong> message" % code.replace("-", " ").title()

# Static file
@bottle.route('/static/:path#.+#')
def static_folder(path):
	return static_file(path, root=os.path.join(WWW_ROOT, 'static'))

# Boot
if __name__ == "__main__":
	bottle.debug(True)
	bottle.run(server='gae')