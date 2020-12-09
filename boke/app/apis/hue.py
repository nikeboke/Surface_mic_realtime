
from flask import Blueprint, request, jsonify
import phue

hue = Blueprint('hue', __name__)

try:
    b = phue.Bridge('192.168.1.20')
except:
    b = None
    print('cannot connect to hue bridge')
else:
    try:
        b.connect()
    except:
        print('hue connection error')

@hue.route('/api/hue/setlight', methods=['GET'])
def set_light():
    '''
    args cannot be empty
    gets name as input and command
    returns statuscode
    '''
    cmd = dict(request.args)
    if not cmd:
        return jsonify(success=False), 500

    name = cmd.pop('name')
    for k,v in cmd.items():
        if type(v) == str:
            try:
                int(v)
            except Exception:
                pass
            else:
                cmd[k] = int(v)

    if 'on' in cmd.keys():
        cmd['on'] = cmd['on'].lower() in ['true'] #is True
    if b:
        b.set_light(name, cmd)
        return jsonify(success=True)
    return jsonify(success=False)

@hue.route('/api/hue/getlights')
def get_lights():
    '''
    returns list of light names
    '''
    if b:
        rv = b.get_light_objects('name').keys()
        return jsonify(names=list(rv), success=True)
    return jsonify(names=[], success=False)
