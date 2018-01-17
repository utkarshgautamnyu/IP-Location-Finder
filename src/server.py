import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import httpclient
import os
import json
import re
import pickle
import time

ROOT = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(ROOT, 'templates')
STATIC_DIR = os.path.join(ROOT, 'static')
GOOGLE_MAPS_KEY = 'AIzaSyBZDgontArVnzdUGccBScTPYMQ7pzZnzas'
FREEGEOIP_URL_PATTERN = "http://freegeoip.net/json/%(host)s"
MAX_CACHE_SIZE = 100

cache = dict()

try:
    with open('cache.pickle', 'rb') as handle:
        cache = pickle.load(handle)
except:
    print("Cache is empty")

class APIHandler(tornado.websocket.WebSocketHandler):
    @classmethod
    def is_hostname(cls, s):
        """ Checks if hostname is valid. 
            String following a period should consist of only letters.
        """
        if s.count('.') > 2:
            return False

        pos = s.find('.')
        split_string = s[pos+1:]

        is_host = False
        is_string = False

        if isinstance(s,str):
             is_string = True

        pattern = re.compile(r'^[a-zA-Z\.]+$')

        if pattern.match(split_string):
            is_host = True
        
        return is_string and is_host


    def process_message(self, message):
        msg = json.loads(message)
        if msg['msg'] == 'getPosition':
            self.get_position(msg['payload'])

    def open(self):
        print("Client connected")

    def on_message(self, message):
        self.process_message(message)

    def on_close(self):
        print("WebSocket closed")

    def implement_lru(self):
        """ Implements LRU Cache. Gets the least recently used hostname 
            based on timestamp and deletes it.
        """
        print("Cache full, removing least recently used key")
        lru = min(cache.keys(), key=(lambda k: cache[k].get('timestamp')))
        del cache[lru]
   
    def get_position(self, host_or_ip):
        """  Checks if hostname is available in cache. 
             If available return the position of hostname. 
             Else request hostname from FREEGEOIP asynchronously.
        """

        def handle_response(response):
            """ Asynchronous response handler. 
                Passes response to api.js.
                Checks for cache overflow and calls implement_lru. 
            """
            if len(cache) > MAX_CACHE_SIZE and not found_in_cache:
                self.implement_lru()

            obj = {'response' : response, 'timestamp' : time.time()}
            cache[host_or_ip] = obj
            
            self.write_message({
                'msg': 'position',
                'payload': response.body.decode('utf-8'),
                'hostname' : host_or_ip
            })

        if host_or_ip in cache:
            print("Found in Cache")
            found_in_cache = True
            res = cache.get(host_or_ip)
            response = res.get('response')
            handle_response(response)
        else:
            print("Not Found in Cache, requesting...")
            found_in_cache = False
            client = httpclient.AsyncHTTPClient()
            client.fetch(FREEGEOIP_URL_PATTERN % {'host': host_or_ip}, handle_response)
            

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html", google_maps_key=GOOGLE_MAPS_KEY)

def make_app():
    settings = {
        'debug': True,
        'template_path': TEMPLATE_DIR
    }
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/wsapi/", APIHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, { 'path': STATIC_DIR })
        ], **settings
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()

    except KeyboardInterrupt:
        with open('cache.pickle', 'wb') as handle:
            pickle.dump(cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        tornado.ioloop.IOLoop.current().stop()

