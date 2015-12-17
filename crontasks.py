import time
import webapp2

import logging
from google.appengine.api import mail
from google.appengine.ext import ndb

from main import Cron_Status

class ToggleCronHandler(webapp2.RequestHandler):
  def get(self):
    logging.info("starting cron toggle")

    cronstatus = Cron_Status.query().get()

    logging.info("status was {!s}".format(cronstatus.status))
    cronstatus.status = not cronstatus.status

    cronstatus.put()
    logging.info("status is {!s}".format(cronstatus.status))


    if cronstatus.status:
      self.response.out.write("true")
    else:
      self.response.out.write("false")

class WeeklyEmailHandler(webapp2.RequestHandler):
  def get(self):
    cronstatus = Cron_Status.query().get()
    #if the status entity is false or nonexistant, don't send the email
    if not cronstatus or not cronstatus.status:
      return false
    #otherwise send it
    mail.send_mail('Ben@kerestan1520cron.appspotmail.com', 'timothyrjames@gmail.com', 'hello Tim!', 'This email is sent (via cron) from the webpage at http://kerestan1520.appspot.com!')
    return True

mappings = [
  ('/tasks/weeklyemail', WeeklyEmailHandler),
  ('/tasks/toggle', ToggleCronHandler)
]
app = webapp2.WSGIApplication(mappings, debug=True)