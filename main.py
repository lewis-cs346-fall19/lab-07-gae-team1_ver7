import passwords 
import sys
import MySQLdb
import webapp2
import logging

import random

class AddPersonHandler(webapp2.RequestHandler):
	def get(self):
		conn = MySQLdb.connect(unix_socket = "/cloudsql/electric-folio-258117:us-central1:l2", user = passwords.SQL_USER, passwd = passwords.SQL_PASSWD, db= "db")
		cursor = conn.cursor()

		username=self.request.get('username')
		id = self.request.get('id')
		if username != None:
			cursor.execute("UPDATE sessions SET username = %s WHERE id = %s", (username, id))
			cursor.execute("INSERT INTO users (username, value) VALUES (%s, 0)", (username,))
			self.response.write("your value is 0")
			self.response.write("<form method='get' action='/on_add_value'><input type='submit' value='Increment by 1' name='button'><input  type='hidden' value="+username+" name=username></form>")

			conn.commit()
			conn.close()
		cookie = self.request.cookies.get("cookie")
		if(cookie != None):
			cursor.execute("SELECT username FROM sessions where id = %s", (cookie,))
			username = cursor.fetchall()
			username = username[0][0]
			cursor.execute("SELECT value FROM users WHERE username = %s", (username,))
			self.response.write("your val is " + str(cursor.fetchall()[0][0]))

class AddValueHandler(webapp2.RequestHandler):
	def get(self):
		conn = MySQLdb.connect(unix_socket = "/cloudsql/electric-folio-258117:us-central1:l2", user = passwords.SQL_USER, passwd = passwords.SQL_PASSWD, db= "db")
		cursor = conn.cursor()
		username = self.request.get('username')
		button = self.request.get('button')
		if button != None:
			#print("username", username)
			cursor.execute("SELECT value FROM users WHERE username = %s", (username,))
			results = cursor.fetchall()

			if(len(results) > 0):
				val = results[0][0]
				val = int(val)
			else:
				val = 0

			cursor.execute("UPDATE users SET value = %s WHERE username = %s", (val + 1, username))

			conn.commit()
			self.response.write("your val is " + str(val))

			conn.close()

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers["Content-Type"] = "text/html"
		conn = MySQLdb.connect(unix_socket = "/cloudsql/electric-folio-258117:us-central1:l2", user = passwords.SQL_USER, passwd = passwords.SQL_PASSWD, db= "db")
		cursor = conn.cursor()

		self.response.write( "<html>")
		self.response.write( "<head>")
		self.response.write( "<title>First GAE DB Script</title>")
		self.response.write( "</head>")
		self.response.write( "<body>")
		username = self.request.get('username')
		id = self.request.get("id")
		button = self.request.get("button")
		cookie = self.request.cookies.get("cookie")
		if cookie == None:
			id = "%032x" % random.getrandbits(128)
			cursor.execute("INSERT INTO sessions(id) VALUES (%s);", (id,))
			cursor.close()
			self.response.set_cookie("cookie", id, max_age=1800)
			self.response.write("<form method ='get' action='/on_add_person'>")
			self.response.write("<input type='text' name='username'>")
			self.response.write("<input type='hidden' name ='id' value = " + str(id) + ">")
			self.response.write("<input type='submit'>")
			self.response.write("</form>")
		else:
			cursor.execute("SELECT username FROM sessions where id = %s", (cookie,))
			username = cursor.fetchall()
			username = username[0][0]
			cursor.execute("SELECT value FROM users WHERE username = %s", (username,))
			self.response.write("your val is " + str(cursor.fetchall()[0][0]))
		conn.commit()
		conn.close()


		self.response.write("</body>")
		self.response.write("</html>")


app = webapp2.WSGIApplication([
    ("/", MainPage), ('/on_add_person', AddPersonHandler),  ('/on_add_value', AddValueHandler)
], debug=True)


