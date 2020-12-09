from flask import Blueprint, request, jsonify
import asyncio
import requests
host = '127.0.0.1:5000'
import threading
import time

events = Blueprint('events', __name__)

class Event:
    _events = []

    def __init__(self, device_name, trigger, action):
        self.id = len(Event._events)
        self.label = f"Event {self.id}"
        self.device_name = device_name
        self.trigger = trigger
        self.action = action

        self.is_active = False


    def start(self):
        if self.is_active:
            self.stop()

        self.is_active = True
        self.thread = threading.Thread(target=self.job, daemon=True)
        self.thread.start()
        print(f'start event {self.id} ')

    def stop(self):
        self.is_active = False
        self.thread.join()
        print(f'stop event {self.id} ')

    @staticmethod
    def get_events():
        if not Event._events ==  Event.from_file():
            Event._events = Event.from_file()
        return Event._events

    def save_to_file(self):
        import pickle
        events = self.from_file()
        with open('./events.pck', 'wb') as f:
            if self not in events:
                events.append(self)
            else:
                events.remove(self)
                events.append(self)
            pickle.dump(events, f)

    @staticmethod
    def from_file(filename='./events.pck'):
        ''' returns all events from pickle file '''
        import pickle
        _all = []
        import os
        if not os.path.isfile(filename):
            return []

        with open(filename, 'rb') as f:
            while True:
                try:
                    rv = pickle.load(f)
                    _all.extend(rv)
                except Exception as e:
                    break
        return _all

    def __eq__(self, other):
        if type(self) == type(other):
            return self.id == other.id
        return False

    def __repr__(self):
        return f'Event(id={self.id}, {self.device_name}, {self.trigger}, {self.action})'

    def _delete_all(self):
        import os
        os.remove('./events.pck')

    def delete(self):
        ''' delete event from file'''
        if self.is_active:
            self.stop()
        self._delete_all()
        self._events.pop(self.id)
        for i in range(len(self._events)):
            e = self._events[i]
            e.id = i
            e.save_to_file()

    def job(self):
            while self.is_active:
                    try:
                            time.sleep(0.5)
                            cond = self.trigger()
                    except Exception as e:
                            print(e)
                    else:
                            if cond:
                                    self.action(self.device_name)

class Trig:
    n = 0
    def __init__(self, n, desc):
        self.n = n
        self.desc = desc
        self.id = Trig.n
        Trig.n += 1

    def __call__(self):
        return self.cond()

    def __str__(self):
        return self.desc

    def cond(self):
        return requests.get(f'http://{host}/api/predict').json()['points'][0] == self.n

import abc
class Action(abc.ABC):
    n = 0
    def __init__(self, desc):
        self.desc = desc
        self.id = Action.n
        Action.n += 1

    def __str__(self):
        return self.desc

class HueAction(Action):

    def __init__(self, params, desc):
        self.params = params
        super().__init__(desc)

    def __call__(self, dev_name):
        self.params['name'] = dev_name
        requests.get(f'http://{host}/api/hue/setlight', params=self.params)

class SmsAction(Action):
    pass

def get_devices():
    names = requests.get(f'http://{host}/api/hue/getlights').json()['names']
    return names

trig1 = Trig(1, 'if predict == 1')
trig2 = Trig(2, 'if predict == 2')
trig3 = Trig(3, 'if predict == 3')
trig4 = Trig(4, 'if predict == 4')

action1 = HueAction({"on" : True, "bri" : 0}, 'turn on bri:0')
action2 = HueAction({"on" : True, "bri" : 254}, 'turn on bri:full')
action3 = HueAction({"on" : True, "bri" : 100, 'transitiontime':500}, 'turn on bri:100 delay:500')
action4 = HueAction({"on" : False, "bri" : 0}, 'turn off')


#used for pickle load
import sys
sys.modules['__main__'].Event = Event
sys.modules['__main__'].Trig = Trig
sys.modules['__main__'].Action = Action
sys.modules['__main__'].HueAction = HueAction
sys.modules['__main__'].trig1 = trig1
sys.modules['__main__'].trig2 = trig2
sys.modules['__main__'].trig3 = trig3
sys.modules['__main__'].trig4 = trig4
sys.modules['__main__'].action1 = action1
sys.modules['__main__'].action2 = action2
sys.modules['__main__'].action3 = action3
sys.modules['__main__'].action4 = action4
sys.modules['__main__'].get_devices = get_devices


#event_list = Event.from_file()
actions = [action1, action2, action3, action4]
trigs = [trig1, trig2, trig3, trig4]

@events.route('/api/events/setevent', methods=['GET', 'POST'])
def set_event():
    _id = int(request.args.get('id'))
    event = Event.get_events()[_id]
    if event:
        is_active = request.args.get('active')
        if is_active:
            is_active = is_active.lower() == 'true'
            if is_active:
                event.start()
            else:
                event.stop()

    return jsonify({'success' : True})


@events.route('/api/events/createevent')
def create_event():
    dev_name = request.args.get('dev_name')
    trig_id = int(request.args.get('trig_id'))
    action_id = int(request.args.get('action_id'))

    event = Event(dev_name, trigs[trig_id], actions[action_id])
    event.save_to_file()
    return jsonify({'success' : True})

@events.route('/api/events/deleteevent')
def delete_event():
    _id = int(request.args.get('id'))
    event = Event.get_events()[_id]
    event.delete()
    return jsonify({'success' : True})

def _close():
    for e in Event.from_file():
        if e.is_active:
            e.stop()

import atexit
atexit.register(_close)
'''
if __name__ == '__main__':
    names = get_devices()
    e1 = Event(names[1], trig2, action2)
    e2 = Event(names[1], trig4, action4)
    e1.save_to_file()
    e2.save_to_file()
'''

