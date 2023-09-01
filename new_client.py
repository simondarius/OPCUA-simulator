from flask import Flask,render_template,jsonify,request,url_for
from server_builders import Adaptronic
#<==== Server Builders =====>
server_objects=list()

app= Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',js_file_url=url_for('static',filename='client.js'))
@app.route('/New_Instance',methods=['POST','OPTIONS'])
def createInstance():
    global server_objects
    if request.method=='POST':
        try:     
            new_server=Adaptronic()    
            server_objects.append(new_server)
            return jsonify({'response':'OK','server_url':"localhost:6000",'error_message':'nO error message my nigga','server_number':1})
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
            message=server_objects[to_update].simulate(data['SFC'],data['Material_Number'],data['NC_CODE'])
            return message
        except Exception as e: 
            
            return jsonify({'response':'NOK','server_url':None,'error_message':str(e)+f', when trying to acces index {to_update}, lenght is {len(server_objects)}','server_number':None})
    else: return jsonify({'response':'METHOD NOT ALLOWED!'})
        
app.run(debug=True)
