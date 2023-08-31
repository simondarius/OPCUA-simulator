# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 09:33:43 2023

@author: dsimon
"""

from flask import Flask,render_template,jsonify,request
from opcua import Server,Client
from opcua import ua
from threading import Thread,Event,Lock
#<==== Server Builders =====>
port=6000;
current_threads=list()
thread_events=list()
thread_counter=0
server_objects=list()

class base_server:
    def __init__(self):
        global port;
        self.server=Server()
        self.url=f"opc.tcp://localhost:{port}"
        self.server.set_endpoint(self.url)
        
        port+=100
        self.namespace=self.server.register_namespace('OPCUA_SERVER')
    
            
            
        
class Adaptronic(base_server):
    def __init__(self):
        super().__init__()
        
        
        self.SFC_value=""
        self.Testresult_value=""
        self.SAP_Errormessage_value=""
        self.Error_NC_Code_value=""
        self.Testprotocol_value=""
        self.Material_Number_value=""
        
        node=self.server.get_objects_node()
        Param=node.add_object(self.namespace,"Parameters")
        
        self.SFC=Param.add_variable(self.namespace, "SFC", self.SFC_value)
        self.SFC.set_writable();
        self.Testresult = Param.add_variable(self.namespace, "Testresult",self.Testresult_value)
        self.SAP_Errormessage = Param.add_variable(self.namespace, "SAP_Errormessage",self.SAP_Errormessage_value)
        self.SAP_Error_NC_Code = Param.add_variable(self.namespace, "SAP_Error_NC_Code",self.Error_NC_Code_value)
        self.Testprotocol = Param.add_variable(self.namespace, "Testprotoco",self.Testprotocol_value)
        self.Material_Number = Param.add_variable(self.namespace, "Material_Number", self.Material_Number_value)
    def serverLoop(self,stop_event):
        self.server.start()
        try:
            while not stop_event.is_set():
                pass
        finally:
            self.server.stop()
    def simulate(self,SFC):
        try:
            client=Client(self.url)
            client.connect()
            
            sfc_node = client.get_node("ns=2;s=Parameters.SFC")
            new_sfc_value = str(SFC)
            sfc_node.set_value(new_sfc_value)
                
            client.disconnect()
            return jsonify({'response':'OK','message':f'Successfully ran SFC {SFC} through server at {self.url}','error_message':'No error'})                 
        except Exception as e:
            return jsonify({'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'})
    def updateSelf(self,SFC):
        
        client=Client(self.url)
        client.connect()
        
        sfc_node = client.get_node("ns=2;s=Parameters.SFC")
        new_sfc_value = str(SFC)
        sfc_node.set_value(new_sfc_value)
            
        client.disconnect()

app= Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/New_Instance',methods=['POST','OPTIONS'])
def createInstance():
    global port
    global current_threads
    global thread_counter
    global thread_events
    global server_objects
    
    if request.method=='POST':
        try:
            thread_events.append(Event())
            new_server=Adaptronic()
            
            server_objects.append(new_server)
            current_threads.append(Thread(target=server_objects[thread_counter].serverLoop,args=(thread_events[thread_counter],)))
            current_threads[thread_counter].start()
            thread_counter+=1
     
            return jsonify({'response':'OK','server_url':server_objects[thread_counter-1].url,'error_message':'nO error message my nigga','server_number':thread_counter})
        except Exception as e: 
     
            return jsonify({'response':'NOK','server_url':None,'error_message':'Here'+str(e),'server_number':None})
    else: return jsonify({'response':'METHOD NOT ALLOWED!'})  
    


@app.route('/Delete_Instance', methods=['POST', 'OPTIONS'])
def deleteInstance():
    global current_threads
    global thread_counter
    global thread_events
    global server_objects
    if request.method == 'POST':
        try:
            data = request.json
            to_delete = data['to_delete']  
            
            if 0 <= to_delete < len(current_threads):
               
                thread_events[to_delete].set()
                current_threads[to_delete].join()
                current_threads.pop(to_delete)
                server_objects[to_delete].join()
                server_objects.pop(to_delete)
                thread_events.pop(to_delete)
                thread_counter -= 1
                
                return jsonify({'response': 'OK', 'message': 'Thread deleted successfully'})
            else:
                return jsonify({'response': 'NOK', 'message': 'Invalid thread index'})

        except Exception as e:
            return jsonify({'response': 'NOK', 'message': str(e)})
    else:
        return jsonify({'response': 'METHOD NOT ALLOWED!'})


@app.route('/Run_Instance',methods=['POST','OPTIONS'])
def runInstance():
    global server_objects
    if request.method=='POST':
        try:
            data=request.json
            to_update=data['to_update']
            message=server_objects[to_update].simulate(data['SFC'])
            
            return message
        except Exception as e: 
            
            return jsonify({'response':'NOK','server_url':None,'error_message':str(e)+f', when trying to acces index {to_update}, lenght is {len(server_objects)}','server_number':None})
    else: return jsonify({'response':'METHOD NOT ALLOWED!'})
        
app.run(debug=True)
