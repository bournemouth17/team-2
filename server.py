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

def get_spolunteer_data(o):
    user = dict(
        fname = o.get_argument('fname', ''),
        lname = o.get_argument('lname', ''),
        known = o.get_argument('known', ''),
        age = o.get_argument('age', ''),
        gender = o.get_argument('gender', ''),
        phone = o.get_argument('phone', ''),
        email = o.get_argument('email', ''),
        address = o.get_argument('address', ''),
        kin_name = o.get_argument('kin_name', ''),
        kin_relationship = o.get_argument('kin_relationship', ''),
        kin_phone = o.get_argument('kin_phone', ''),
        outdoor = o.get_argument('outdoor', ''),
        indoor = o.get_argument('indoor', ''),
        interests = o.get_argument('indoor', ''),
        date = datetime.datetime.now().strftime('%m/%d/%Y'),
    )
    return user

class AuthTrackerHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', ''),
        col = self.application.db['daily']
        doc = col.find_one({'email': email[0]})
        doc = col.find({'email': email[0]}).sort({'_id':-1}).limit(1)
        if doc:
            if doc['stage'] == 5:
                self.write({'status':1})
            else:
                self.self.write({'status':0, 'message': 'not in operation'})
        self.self.write({'status':0, 'message': 'not checked in'})

class HomePageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class FormPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('forms_wizard.html')

class SignUpHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('forms_wizard.html')

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
            interests = self.get_argument('interests', ''),
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



class GetUserDetailsHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', '')
        col = self.application.db['spolunteer']
        doc = col.find_one({'email': email[0]})
        if doc:
            self.write({'status':1, 'user':doc})
        else:
            self.write({'status':0, 'message':'no such user'})

class GetUserActivityHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', '')
        col_1 = self.application.db['spolunteer']
        col_2 = self.application.db['daily']
        doc_1 = col_1.find_one({'email': email[0]})
        doc_2 = col_2.find_one({'email': email[0]})
        if doc_1 and doc_2:
            del doc_1['_id']
            del doc_2['_id']
            del doc_2['email']
            result = doc_1.copy()
            result.update(doc_2)
            self.write({'status':1, 'user': result})
        else:
            self.write({'status':0, 'message':'no such user'})

class EditUserHandler(tornado.web.RequestHandler):
    def post(self):
        col = self.application.db['daily']
        email = self.get_argument('email', '')

        user = { k: self.get_argument(k) for k in self.request.arguments }

class SearchBySkillHandler(tornado.web.RequestHandler):
    def post(self):
        col = self.application.db['spolunteer']
        skill = self.get_argument('skill', '')
        doc = col.find({"interests":{"$regex": skill}})
        print doc
        self.write({'status':1})

# class DemoHandler(tornado.web.RequestHandler):
#     def get(self):
#         argument = self.get_argument('key', 'default_value')
#         self.write(argument)
#
# class PatternHandler(tornado.web.RequestHandler):
#     def get(self, input_text):
#         col = self.application.db['my_collection']
#         doc = col.find_one({'key': input_text})
#         if doc:
#             del doc['_id']
#             self.write(doc)
#         else:
#             self.set_status(404)
#
#     def post(self, input_text):
#         new_value = self.get_argument('value')
#         col = self.application.db['my_collection']
#         doc = col.find_one({'key': input_text})
#         if doc:
#             doc['value'] = new_value
#             col.save(doc)
#         else:
#             doc = {'key': input_text, 'value': new_value}
#             col.insert(doc)
#         del word_doc["_id"]
#         self.write(doc)

class Application(tornado.web.Application):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['cfg17']

        handlers = [
            (r"/", HomePageHandler),
            (r"/forms_wizard", SignUpHandler),
            # (r"/signup", FormPageHandler),
            (r"/checkin", CheckInHandler),
            (r"/checkout", CheckOutHandler),
            (r"/assets/(.*)", tornado.web.StaticFileHandler,
             {"path": os.path.join(os.path.dirname(__file__), "frontend/assets")}),
            (r"/bower_components/(.*)", tornado.web.StaticFileHandler,
             {"path": os.path.join(os.path.dirname(__file__), "frontend/bower_components")}),
             (r"/authtracker", AuthTrackerHandler),
            # (r"/demo", DemoHandler),
            # (r"/pattern(\w+)", PatternHandler),
            # (r"/files/(.*)", tornado.web.StaticFileHandler,
            #  {"path": os.path.join(os.path.dirname(__file__), "files")}),
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "frontend"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug = True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
