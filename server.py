import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os
from pymongo import MongoClient
import json
import datetime

define("port", default=8000, help="run on the given port", type=int)

class SignUpHnadler(tornado.web.RequestHandler):
    def post(self):
        user = dict(
            fname = self.get_argument('fname', ''),
            lname = self.get_argument('lname', ''),
            known = self.get_argument('known', ''),
            age = self.get_argument('age', ''),
            gender = self.get_argument('gender', ''),
            phone = self.get_argument('phone', ''),
            email = self.get_argument('email', ''),
            address = self.get_argument('address', ''),
            kin_name = self.get_argument('kin_name', ''),
            kin_relationship = self.get_argument('kin_relationship', ''),
            kin_phone = self.get_argument('kin_phone', ''),
            outdoor = self.get_argument('outdoor', ''),
            indoor = self.get_argument('indoor', ''),
            interests = self.get_argument('indoor', ''),
            date = datetime.datetime.now().strftime('%m/%d/%Y'),
        )
        print user
        col = self.application.db['spolunteer']
        doc = col.find_one({'email': user['email']})
        if doc:
            self.write({'status':0, 'message': 'already registered'})
        else:
            col.insert(user)
            self.write({'status':1})

class CheckInHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', ''),
        col_from = self.application.db['spolunteer']
        col_to = self.application.db['daily']
        doc = col_from.find_one({'email': email[0]})
        if doc:
            del doc['_id']
            user_day = {
                'email':doc['email'],
                'stage': 1,
                'date': datetime.datetime.now().strftime('%m/%d/%Y'),
                'checkin' : datetime.datetime.now().strftime('%H:%M'),
            }
            col_to.insert(user_day)
            self.write({'status':1,'user':doc})
        else:
            self.write({'status':0,'message':'not registered'})

class CheckOutHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', ''),
        col = self.application.db['daily']
        doc = col.find_one({'email': email[0]})
        if doc:
            doc['checkout'] = datetime.datetime.now().strftime('%H:%M')
            doc['stage'] = 0
            col.save(doc)
            self.write({'status':1})
        else:
            self.write({'status':0,'message':'not checked in'})

class DemoHandler(tornado.web.RequestHandler):
    def get(self):
        argument = self.get_argument('key', 'default_value')
        self.write(argument)

class PatternHandler(tornado.web.RequestHandler):
    def get(self, input_text):
        col = self.application.db['my_collection']
        doc = col.find_one({'key': input_text})
        if doc:
            del doc['_id']
            self.write(doc)
        else:
            self.set_status(404)

    def post(self, input_text):
        new_value = self.get_argument('value')
        col = self.application.db['my_collection']
        doc = col.find_one({'key': input_text})
        if doc:
            doc['value'] = new_value
            col.save(doc)
        else:
            doc = {'key': input_text, 'value': new_value}
            col.insert(doc)
        del word_doc["_id"]
        self.write(doc)

class Application(tornado.web.Application):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['cfg17']

        handlers = [
            (r"/signup", SignUpHnadler),
            (r"/checkin", CheckInHandler),
            (r"/checkout", CheckOutHandler),
            (r"/demo", DemoHandler),
            (r"/pattern(\w+)", PatternHandler),
            (r"/files/(.*)", tornado.web.StaticFileHandler,
             {"path": os.path.join(os.path.dirname(__file__), "files")}),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug = True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
