from flask import Flask,render_template,request,jsonify,url_for
from server_builders import Adaptronic
from flask_socketio import SocketIO
from flask_cors import CORS
import json
import logging
#<==== Server Builders =====>
server_objects=list()

app= Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}) 
socket = SocketIO(app, cors_allowed_origins="*")  
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
app.logger.addHandler(logging.StreamHandler())

@app.route('/')
def index():
    return render_template('index.html',js_file_url=url_for('static',filename='client.js'))

    
@socket.on('connect')
def socket_connect():
    app.logger.info('Client connected!')
    socket.emit('message',json.dumps({'flag':'RefreshInterface','info':[server.url for server in server_objects]}))
@socket.on('message')
def handle_request(data):
    global server_objects
    app.logger.info('Received an message')
    message=json.loads(data)
    flag=message['flag']
    if flag=='DeleteInstance':
        try:
            index=int(message['index'])
            server=server_objects.pop(index)
            server.stop_event.set()
            del server
            socket.emit('message',json.dumps({'flag':'DeleteInstanceOK','info':'None','index':index}))
        except Exception as e:
            socket.emit('message',json.dumps({'flag':'DeleteInstanceNOK','info':str(e)}))

    if flag=='NewInstance':
        try:
            assert(message['type'] in ['Adaptronic'])
            if(message['type']=='Adaptronic'):new_server=Adaptronic()
            server_objects.append(new_server)
            socket.emit('message',json.dumps({'flag':'NewInstanceOK','info':str(new_server.url)}))
        except Exception as e:            
            socket.emit('message',json.dumps({'flag':'NewInstanceNOK','info':str(e)}))

    if flag=='RunInstance':
        try:
            index=int(message['index'])
            print(index)
            assert(message['type'] in ['Adaptronic'])
            if(message['type']=='Adaptronic'):
                result=server_objects[index].simulate(message['SFC'],message['MatNumber'],message['NC_CODE'])
                result='tmp'
                socket.emit('message',json.dumps({'flag':'RunInstanceOK','info':str(result)}))
        except Exception as e:
                        
            socket.emit('message',json.dumps({'flag':'RunInstanceNOK','info':str(e)}))


socket.run(app,debug=True)
