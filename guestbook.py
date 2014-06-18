#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cgi #import module cgi
import urllib #import library urllib
from google.appengine.api import users #using the users service (connect with account google)
from google.appengine.ext import ndb #using python NDB datastore

import webapp2

#define html footer template:

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
        <div><textarea name="content" rows="30" cols="60"></textarea></div>
        <div><input type="submit" value="Ký vào lưu bút"></div>
    </form>
    <form>Tên lưu bút:
        <input value="%s" name="guestbook_name">
        <input type="submit" value="Thay đổi ">
    </form>
    <a href="%s">%s</a>
    </body>
</html>
"""

#define default guestbook name:
DEFAULT_GUESTBOOK_NAME= 'default_guestbook'

#function guest book_key is for create a datastore key for a Guestbook entity with guestbook_name
def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    return ndb.Key('Guestbook', guestbook_name)

#class Greeting(author, content, date)
class Greeting(ndb.Model):
    author = ndb.UserProperty() #user object
    content = ndb.StringProperty(indexed=False)#unicode string; up to 500 characters, non-indexed
    date = ndb.DateTimeProperty(auto_now_add=True)#date and time

#main
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        #Get all greetings whose guest book name is guestbook_name and sort by date
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        #Get 10 results from greetings_query
        greetings = greetings_query.fetch(10)

        #print results
        for greeting in greetings:
            if greeting.author:
                 self.response.write(
                    'Vào <i>%s</i></br><b>%s</b> đã viết:' %(greeting.date, greeting.author)

                )
            else:
                self.response.write('Vào <i>%s</i></br>Một khách đã viết:' %greeting.date)
            self.response.write('<blockquote>%s</blockquote>' %cgi.escape(greeting.content))

        #check whether login or not
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Đăng xuất'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Đăng nhập'

        #write the submission form that we have defined on the top of the script.
        sign_query_params = urllib.urlencode({'guestbook_name': guestbook_name})
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE %(sign_query_params, cgi.escape(guestbook_name), url, url_linktext))
#class Guestbook, when user click submit button, this class will be run
class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user()
        greeting.content = self.request.get('content')
        greeting.put()
        query_params = {'guestbook': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))
#application
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)