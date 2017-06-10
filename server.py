import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os
from pymongo import MongoClient
import json
import datetime
import tornado.websocket

define("port", default=8000, help="run on the given port", type=int)

websocket_clients = set()

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
        email = self.get_argument('email', '')
        col = self.application.db['daily']
        doc = col.find_one({'email': email})
        # doc = col.find({'email': email[0]}).sort({'_id':-1}).limit(1)
        if doc:
            if doc['stage'] == 5:
                self.write({'status':1})
            else:
                self.self.write({'status':0, 'message': 'not in operation'})
        self.write({'status':0, 'message': 'not checked in'})

class MapSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        websocket_clients.add(self)
        col_1 = self.application.db['tracking']
        col_2 = self.application.db['daily']
        doc = col_1.find()
        results = []
        for item in response:
            active = col_2.find({'email':item['email'],'stage': { '$ne' : 0 }})
            if active:
                results.append({
                    'coordinates':[item['lat'],item['lon']],
                    'email':item['email'],
                    'armband':item['armband']
                })
        self.write_message({'results': results})
        print("WebSocket opened")

    def on_message(self, message):
        pass
        # self.write_message(u"You said: " + message)

    def on_close(self):
        websocket_clients.remove(self)
        print("WebSocket closed")

class GpsHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email','')
        armband = self.get_argument('bandno','')
        lat = self.get_argument('lat','')
        lon = self.get_argument('lon','')
        col = self.application.db['tracking']
        doc = col.find_one({'email': email})
        print email
        print lat
        print lon
        print doc
        if doc:
            doc['lat'] = lat
            doc['lon'] = lon
            print doc
            col.save(doc)
        else:
            doc = {'email': email, 'lat': lat, 'lon': lon}
            print doc
            col.insert(doc)
        for ws_client in websocket_clients:
            ws_client.write_message({
                'coordinates':[lat,lon],
                'email':email,
                'armband':armband
            })
        self.write({'status':1})

class DangerHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email','')
        lat = self.get_argument('lat','')
        lon = self.get_argument('lon','')
        col = self.application.db['danger']
        doc = {'email': email, 'lat': lat, 'lon': lon}
        col.insert(doc)
        self.write({'status':1})

class HomePageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

class CheckinPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('plugins_datatables.html')

    def post(self):
        email = self.get_argument('email', '')
        armband = self.get_argument('arnumber', '')
        col_from = self.application.db['spolunteer']
        col_to = self.application.db['daily']
        doc = col_from.find_one({'email': email})
        if doc:
            del doc['_id']
            user_day = {
                'email':doc['email'],
                'stage': 1,
                'armband' : armband,
                'date': datetime.datetime.now().strftime('%m/%d/%Y'),
                'checkin' : datetime.datetime.now().strftime('%H:%M'),
            }
            col_to.insert(user_day)
            self.write({'status':1,'user':doc})
        else:
            self.write({'status':0,'message':'not registered'})

class CheckoutPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('check_out.html')

    def post(self):
        email = self.get_argument('email', '')
        col = self.application.db['daily']
        # doc = col.find_one({'email': email})
        doc = col.find({'email': email}).sort('_id',-1).limit(1)[0]
        if doc:
            doc['checkout'] = datetime.datetime.now().strftime('%H:%M')
            doc['stage'] = 0
            doc['armband'] = ''
            col.save(doc)
            self.write({'status':1})
        else:
            self.write({'status':0,'message':'not checked in'})

class UserInfoPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('user_info.html')

    def post(self):
        email = self.get_argument('email', '')
        col = self.application.db['spolunteer']
        doc = col.find_one({'email': email})
        print email
        print doc
        if doc:
            del doc['_id']
            self.write({'status':1, 'user':doc})
        else:
            self.write({'status':0, 'message':'no such user'})

class EditUserInfoHandler(tornado.web.RequestHandler):
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
        col = self.application.db['spolunteer']
        col.update_one({'email':user['email']},{'$set':user})
        self.write({'status':1})

class FormPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('forms_wizard.html')

class GuidancePageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('guidance.html')

class TrainingPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('training.html')

    def post(self):
        email = self.get_argument('email', '')
        training = self.get_argument('training', '')
        col = self.application.db['daily']
        doc = col.find_one({'email': email, 'stage' : 2 })
        if doc:
            doc['training'] = training
            doc['stage'] = 3
            col.save(doc)
            self.write({'status':1})
        else:
            self.write({'status':0,'message':'unavailable'})

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

class StartPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('start_task.html')

class FinishPageHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('finish_task.html')

class RTTrackingHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('map.html')

class TaskStatusHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', '')
        status = self.get_argument('status', '')
        col = self.application.db['daily']
        doc = col.find({'email': email}).sort('_id',-1).limit(1)[0]
        if doc:
            if status == 'start':
                doc['stage'] = 5
            else:
                doc['stage'] = 4
            col.save(doc)
            self.write({'status':1})
        else:
            self.write({'status':0,'message':'unavailable'})


class GetUserActivityHandler(tornado.web.RequestHandler):
    def post(self):
        email = self.get_argument('email', '')
        col_1 = self.application.db['spolunteer']
        col_2 = self.application.db['daily']
        doc_1 = col_1.find_one({'email': email})
        doc_2 = col_2.find_one({'email': email})
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
            (r"/checkin", CheckinPageHandler),
            (r"/checkout", CheckoutPageHandler),
            (r"/userinfo", UserInfoPageHandler),
            (r"/guidance", GuidancePageHandler),
            (r"/training", TrainingPageHandler),
            (r"/gps", GpsHandler),
            (r"/useredit", EditUserInfoHandler),
            (r"/start", StartPageHandler),
            (r"/finish", FinishPageHandler),
            (r"/hold", TaskStatusHandler),
            # (r"/volunteers", ManageVolunteersPageHandler),
            (r"/danger", DangerHandler),
            (r"/assets/(.*)", tornado.web.StaticFileHandler,
             {"path": os.path.join(os.path.dirname(__file__), "frontend/assets")}),
            (r"/bower_components/(.*)", tornado.web.StaticFileHandler,
             {"path": os.path.join(os.path.dirname(__file__), "frontend/bower_components")}),
             (r"/authtracker", AuthTrackerHandler),
             (r"/map",MapSocketHandler),
             (r"/rtmap",RTTrackingHandler),
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
