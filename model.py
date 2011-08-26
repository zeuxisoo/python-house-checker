from google.appengine.ext import db

class house_number(db.Model):
	subject = db.StringProperty()
	current_number = db.IntegerProperty()
	create_at = db.DateTimeProperty(auto_now_add=True)