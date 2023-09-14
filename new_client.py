from flask import Flask,render_template,url_for
from server_builders import Adaptronic,Tsk,Telsonic,Arburg
from flask_socketio import SocketIO
from flask_cors import CORS
import json
import logging
from engineio.async_drivers import gevent
import threading
import time
#<==== Server Builders =====>
server_objects_adaptronic=list()
server_objects_tsk=list()
server_objects_telsonic=list()
server_objects_arburg=list()
app= Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}) 
socket = SocketIO(app, cors_allowed_origins="*",async_mode='gevent')  
logging.basicConfig(level=logging.WARNING, handlers=[logging.StreamHandler()])
app.logger.addHandler(logging.StreamHandler())

def RunInstanceWrapper(message):
        try:
            index=int(message['index'])
            type=message['type']
            app.logger.warning(f'Running instance at server of index, type is {type} : {index}')
            assert(type in ['Adaptronic','Tsk','Telsonic','Arburg'])
            if(type=='Adaptronic'):
                result=server_objects_adaptronic[index].simulate(message['SFC'],message['MatNumber'],message['NC_CODE'])
               
                socket.emit('message',json.dumps({'flag':'RunInstanceOK','info':str(result)}))
            elif(type=='Tsk'):
                result=server_objects_tsk[index].simulate(message['SFC'],message['NC_CODE'])
               
                socket.emit('message',json.dumps({'flag':'RunInstanceOK','info':str(result)}))
            elif(type=='Telsonic'):
            
                result=server_objects_telsonic[index].simulate(message['Barcode'],message['Errorcode'])
                print(result)
                socket.emit('message',json.dumps({'flag':'RunInstanceOK','info':str(result)}))        
        except Exception as e:
                app.log_exception(e)
                socket.emit('message',json.dumps({'flag':'RunInstanceNOK','info':str(e)}))
RunningInstances=list()
@app.route('/')
def index():
    return render_template('index.html',js_file_url=url_for('static',filename='client.js'),
                           green_logo_url=url_for('static',filename='logo_green.png'),blue_logo_url=url_for('static',filename='logo.png'),
                           red_logo_url=url_for('static',filename='logo_red.png'),light_logo_url=url_for('static',filename='logo_light.png'))

    
@socket.on('connect')
def socket_connect():
    global server_objects_adaptronic
    global server_objects_tsk
    global server_objects_telsonic
    global server_objects_arburg
    app.logger.info('Client connected!')
    socket.emit('message',json.dumps({'flag':'RefreshInterface','target':'Adaptronic','info':[server.url for server in server_objects_adaptronic]}))
    time.sleep(0.5)
    socket.emit('message',json.dumps({'flag':'RefreshInterface','target':'Tsk','info':[server.url for server in server_objects_tsk]}))
    time.sleep(0.5)
    socket.emit('message',json.dumps({'flag':'RefreshInterface','target':'Telsonic','info':[server.url for server in server_objects_telsonic]}))
    time.sleep(0.5)
    socket.emit('message',json.dumps({'flag':'RefreshInterface','target':'Arburg','info':[server.url for server in server_objects_arburg]}))
@socket.on('message')
def handle_request(data):
    global server_objects_adaptronic
    global server_objects_tsk
    global server_objects_telsonic
    global server_objects_arburg

    app.logger.info('Received an message')
    message=json.loads(data)
    flag=message['flag']
    if flag=='DeleteInstance':
        try:
            server=None
            index=int(message['index'])
            if(message['type']=='Adaptronic'):
                server=server_objects_adaptronic.pop(index)
            elif(message['type']=='Tsk'):
                server=server_objects_tsk.pop(index)
            elif(message['type']=='Telsonic'):
                server=server_objects_telsonic.pop(index)
            elif(message['type']=='Arburg'):
                server=server_objects_arburg.pop(index)              
            server.stop_event.set()
            del server
            socket.emit('message',json.dumps({'flag':'DeleteInstanceOK','info':'None','index':index}))
        except Exception as e:
            socket.emit('message',json.dumps({'flag':'DeleteInstanceNOK','info':str(e)}))

    if flag=='NewInstance':
        try:
          
        
            assert(message['type'] in ['Adaptronic','Tsk','Telsonic','Arburg'])
           
            url='None' 
            if(message['type']=='Adaptronic'):
              
                 new_server=Adaptronic()
               
                 url=new_server.url
                 server_objects_adaptronic.append(new_server)
               
            if(message['type']=='Tsk'):
              
                 new_server=Tsk()
                 url=new_server.url
                
                 server_objects_tsk.append(new_server)

            if(message['type']=='Telsonic'):
              
                 new_server=Telsonic()
                 url=new_server.url
                
                 server_objects_telsonic.append(new_server)     
            if(message['type']=='Arburg'):
                 print('Here,arburg!')
                 new_server=Arburg()
                 url=new_server.url
                
                 server_objects_arburg.append(new_server)     
            
            socket.emit('message',json.dumps({'flag':'NewInstanceOK','info':str(url)}))
        except Exception as e:
           
                      
            socket.emit('message',json.dumps({'flag':'NewInstanceNOK','info':str(e)}))

    if flag=='RunInstance':
        thread=threading.Thread(target=RunInstanceWrapper,args=(message,))
        thread.start()
                                

socket.run(app)
