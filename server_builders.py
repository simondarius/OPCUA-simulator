# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:31:27 2023

@author: dsimon
"""
from opcua import Server,Client
from opcua import ua
import time
from threading import Thread,Event
port=6000
class base_server:
    def __init__(self):
        global port
        self.server=Server()
        self.url=f"opc.tcp://localhost:{port}"
        self.server.set_endpoint(self.url)
        self.PcOResponse=None
        port+=100
        self.namespace=self.server.register_namespace('OPCUA_SERVER')
        self.parameter_list=list()
        self.node=self.server.get_objects_node()
        self.Param=self.node.add_object(self.namespace,"Parameters")
        self.stop_event=Event()
        self.server_thread=Thread(target=self.serverLoop,args=(self.stop_event,))
        self.server_thread.daemon=True
        self.PcOContorllMethod = self.Param.add_method(self.namespace, "PcOControll", self.control_method, [ua.VariantType.Int32], [ua.VariantType.Boolean])
        
    def serverLoop(self,stop_event):
        self.server.start()
        try:
            while not stop_event.is_set():
                pass
        finally:
            self.server.stop()    
            
    def wait_for_PcO(self):
        while(self.PcOResponse==None):
            time.sleep(0.3)
            
    def control_method(self, parent, input_value):
        try:
            self.PcOResponse=input_value
            return [ua.Variant(True,ua.VariantType.Boolean)]
        except:
            return [ua.Variant(False,ua.VariantType.Boolean)]  
        
    def build_parameters(self,names):
        for param in names:
            temp=self.Param.add_variable(self.namespace,str(param),"")
            temp.set_writable(True)
            self.parameter_list.append(temp)
        
    def clear_parameters(self):
        for parameter in self.parameter_list:
            parameter.set_value("")

class Adaptronic(base_server):
    def __init__(self):
        super().__init__()
        
        
        self.NC_DICT={'Testare: Eroare de detectare':'NC0193060000','Testare: Circuit Deschis':'NC0192910000','Testare: Scurtcircuit':'NC0192960000','Testare: Eroare Functionalitate':'NC0192970000',
                      'SFC nu este in asteptare':'NC0003030000','Lipsa parametri proces':'NC0002870000','Parametri proces multiplii':'NC0003040000'}
        
         
        try:
            self.build_parameters(["SFC","TestResult","SAP_Errormessage","SAP_Error_NC_Code","Testprotocol","Material_Number"])
        except Exception as e:
            print(str(e))    
        
        self.server_thread.start()
        return     
    def simulate(self,SFC,MatNumber,NC_CODE):
        self.wait_for_PcO()
        try:
            if(self.PcOResponse==ua.Variant(1, ua.VariantType.Int32)):
                
                self.parameter_list[0].set_value(SFC)
                self.parameter_list[5].set_value(MatNumber)
                if(NC_CODE=='N/A'):
                    self.parameter_list[1].set_value('OK')
                    self.parameter_list[3].set_value('')
                else:
                    self.parameter_list[3].set_value(self.NC_DICT[NC_CODE])
                    self.parameter_list[1].set_value('NOK')
                
            if(self.PcOResponse==ua.Variant(6, ua.VariantType.Int32)):
                pass    
            else:
                raise Exception(f"Invalid PcO response,should have value in [1,6,10] got ({self.PcOResponse})")                 
            self.PcOResponse=None     
        except Exception as e:
            self.PcOResponse=None
            return {'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'}
        
        finally:
            self.wait_for_PcO()
            try:
                if(self.PcOResponse==ua.Variant(10,ua.VariantType.Int32)):
                    self.clear_parameters()     
                else:
                    raise Exception(f"Invalid PcO response,should have value in [1,6,10] got ({self.PcOResponse})")
                self.PcOResponse=None       
            except Exception as e:
                self.PcOResponse=None
                return {'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'}
              
