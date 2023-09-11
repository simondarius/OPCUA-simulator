# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:31:27 2023

@author: dsimon
"""
from opcua import Server
from opcua import ua
import time
from threading import Thread,Event
port=6000
class base_server:
    def __init__(self):
        global port
        self.server=Server()
        self.server.name=f"portServer:{port}"
        self.url=f"opc.tcp://localhost:{port}"
        self.server.set_endpoint(self.url)
        self.PcOResponse=None
        port+=100
        self.namespace=self.server.register_namespace('OPCUA_SERVER#'+str(port))
        self.parameter_list=list()
        self.node=self.server.get_objects_node()
        self.Param=self.node.add_object(self.namespace,"Parameters"+str(port))
        self.stop_event=Event()
        self.server_thread=Thread(target=self.serverLoop,args=(self.stop_event,))
        self.server_thread.daemon=True
        
        
    def serverLoop(self,stop_event):
        self.server.start()
        try:
            while not stop_event.is_set():
                pass
        finally:
            global port
            self.server.stop()    
            
           
        
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
        
        self.PcOContorllMethod = self.Param.add_method(self.namespace, "PcOControll", self.control_method, [ua.VariantType.Int32], [ua.VariantType.Boolean]) 
        try:
            self.build_parameters(["SFC","TestResult","SAP_Errormessage","SAP_Error_NC_Code","Testprotocol","Material_Number"])
        except Exception as e:
            print(str(e))    
        
        self.server_thread.start()
        return    
    def wait_for_PcO(self):
        while(self.PcOResponse==None):
            time.sleep(0.3)
    
    def control_method(self, parent, input_value):
        try:
            self.PcOResponse=input_value
            return [ua.Variant(True,ua.VariantType.Boolean)]
        except:
            return [ua.Variant(False,ua.VariantType.Boolean)]  
     
    def simulate(self,SFC,MatNumber,NC_CODE,scrap_message=""):
        self.clear_parameters()    
        self.parameter_list[0].set_value(SFC)
        self.wait_for_PcO()
        try:
            if(self.PcOResponse==ua.Variant(1, ua.VariantType.Int32)):
                self.parameter_list[5].set_value(MatNumber)
                if(NC_CODE=='N/A'):
                    self.parameter_list[1].set_value('OK')
                    self.parameter_list[4].set_value('')
                else:
                    self.parameter_list[4].set_value(self.NC_DICT[NC_CODE])
                    self.parameter_list[1].set_value('NOK')
                
            elif(self.PcOResponse==ua.Variant(6, ua.VariantType.Int32)):
                self.clear_parameters()    
            elif(self.PcOResponse==ua.Variant(2,ua.VariantType.Int32)):
                self.parameter_list[5].set_value(MatNumber)
                self.parameter_list[1].set_value('NOK')
                     
            else:
                raise Exception(f"Invalid PcO response,should have value in [1,2,6,10] got ({self.PcOResponse})")                 
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
                    raise Exception(f"Invalid PcO response,should have value in [1,2,6,10] got ({self.PcOResponse})")
                self.PcOResponse=None       
            except Exception as e:
                self.PcOResponse=None
                return {'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'}
              
class Tsk(base_server):
    def __init__(self):
        super().__init__()
        
        self.StartTestMethod = self.Param.add_method(self.namespace, "StartTest", self.control_method_StartTest, [ua.VariantType.Int32], [ua.VariantType.Boolean]) 
        self.AcknowledgeMethod = self.Param.add_method(self.namespace, "Acknowledge", self.control_method_Acknowledge, [ua.VariantType.Int32], [ua.VariantType.Boolean]) 
        self.ScrapMethod = self.Param.add_method(self.namespace, "Scrap", self.control_method_Scrap, [ua.VariantType.Int32], [ua.VariantType.Boolean])
        self.StartTestResponse=None
        self.ScrapResponse=None
        self.Acknowledge=None 
        try:
            self.build_parameters(["SFCserialNumber","FinalSerialNumber","TestResult","ErrorCode"])
        except Exception as e:
            print(str(e))    
        temp=self.Param.add_variable(self.namespace,"CurrentTestStep",0)
        temp.set_writable(True)
        self.parameter_list.append(temp)
        self.server_thread.start()
        return    
    def wait_for_Start(self):
        while(self.StartTestResponse==None):
            time.sleep(0.3)
    def wait_for_ScrapOrAcknowledgement(self):
        while(self.Acknowledge==None and self.ScrapResponse==None):
            time.sleep(0.3)
    def control_method_StartTest(self, parent, input_value):
        try:
            self.StartTestResponse=input_value
            return [ua.Variant(True,ua.VariantType.Boolean)]
        except:
            return [ua.Variant(False,ua.VariantType.Boolean)]  
    def control_method_Scrap(self, parent, input_value):
        try:
            self.ScrapResponse=input_value
            return [ua.Variant(True,ua.VariantType.Boolean)]
        except:
            return [ua.Variant(False,ua.VariantType.Boolean)]  
    def control_method_Acknowledge(self, parent, input_value):
        try:
            self.Acknowledge=input_value
            return [ua.Variant(True,ua.VariantType.Boolean)]
        except:
            return [ua.Variant(False,ua.VariantType.Boolean)]       
    def simulate(self,SFC,NC_CODE):
        self.clear_parameters()    
        self.parameter_list[0].set_value(SFC)
        self.parameter_list[4].set_value(150)
        self.wait_for_Start()
        try:
            if(self.StartTestResponse==ua.Variant(1, ua.VariantType.Int32)):
                
                if(NC_CODE=='N/A'):
                    self.parameter_list[2].set_value('OK')
                    self.parameter_list[3].set_value('')
                else:
                    self.parameter_list[3].set_value(NC_CODE)
                    self.parameter_list[2].set_value('NOK')
                self.parameter_list[4].set_value(20000)
                     
            else:
                raise Exception(f"Invalid PcO Start test response,should have value in [1] got ({self.StartTestResponse})")                 
            self.StartTestResponse=None     
        except Exception as e:
            self.StartTestResponse=None
            return {'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'}
        
        finally:
            try:
                self.wait_for_ScrapOrAcknowledgement()
                self.clear_parameters()
                self.ScrapResponse=None
                self.Acknowledge=None      
            except Exception as e:
                self.ScrapResponse=None
                self.Acknowledge=None  
                return {'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'}
              