# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:31:27 2023

@author: dsimon
"""
from opcua import Server
from opcua import ua
import time
from threading import Thread,Event
import random
port=6000
class base_server:
    def __init__(self):
        global port
        self.server=Server()
        self.NC_DICT={'Testare: Eroare de detectare':'NC0193060000','Testare: Circuit Deschis':'NC0192910000','Testare: Scurtcircuit':'NC0192960000','Testare: Eroare Functionalitate':'NC0192970000',
                      'SFC nu este in asteptare':'NC0003030000','Lipsa parametri proces':'NC0002870000','Parametri proces multiplii':'NC0003040000'}
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
        self.parameter_list[4].set_value(100)
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
                    self.parameter_list[3].set_value(self.NC_DICT[NC_CODE])
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
                self.parameter_list[4].set_value(100)
                self.ScrapResponse=None
                self.Acknowledge=None      
            except Exception as e:
                self.ScrapResponse=None
                self.Acknowledge=None  
                return {'response':'NOK','error_message':str(e), 'message': f'Failed to run SFC {SFC} through server at {self.url}'}


class Telsonic(base_server):
    def __init__(self):
        super().__init__()
        try:
            self.build_parameters(["weldBad","weldOk","resultWireBarCode","statusWireBarCode","processStep","cycleTime","distanceAbs","distanceDiff","energy",
                                   "lossPower","maxForce","maxPower","runSpeed","trigDistance","trigForce","trigTime","weldTime"])
        except Exception as e:
            print(str(e))    
        temp=self.Param.add_variable(self.namespace,"errorNumber",0)
        temp.set_writable(True)
        self.parameter_list.append(temp)
        
        self.server_thread.start()
        return    
    def wait_for_ProcessStep(self,for_step):
        while(self.parameter_list[4]!=None):
            time.sleep(0.3)
        
    def simulate(self,Barcode,ErrorCode):
        self.clear_parameters()    
        try:
            for step in range(1,9):
                if step==1:
                    self.parameter_list[4].set_value(str(step))
                elif step==2:
                    self.parameter_list[4].set_value(str(step))
                    self.parameter_list[3].set_value(str(Barcode))
                elif step==3:
                    self.parameter_list[4].set_value(str(step))
                    
                    while(self.parameter_list[4].get_value()!="4"):
                        time.sleep(0.3)
                    
                elif step==4:
                    self.parameter_list[4].set_value(str(step))
                elif step==5:
                    self.parameter_list[4].set_value(str(step))
                elif step==6:
                    self.parameter_list[3].set_value("")
                    self.parameter_list[2].set_value(str(Barcode))
                    self.parameter_list[4].set_value(str(step))
                elif step==7:
                    self.parameter_list[4].set_value(str(step))
                    if(int(ErrorCode) != 0):
                        self.parameter_list[0].set_value("1")
                        self.parameter_list[1].set_value("0")
                          
                    else:
                        self.parameter_list[0].set_value("0")
                        self.parameter_list[1].set_value("1")
                    
                    self.parameter_list[17].set_value(int(ErrorCode))
                    for i in range(0,18):
                        if i==0 or i==1 or i==2 or i==3 or i==4 or i==17:
                            pass
                        else:
                            self.parameter_list[i].set_value(str(random.randint(0,11)))
                            
                else:
                    while(self.parameter_list[4].get_value()!="8"):
                        time.sleep(0.3)
                    self.parameter_list[4].set_value(str(step)) 
                time.sleep(1)

        except Exception as e:
           return {'response':'NOK','error_message':str(e), 'message': f'Failed to run Barcode {Barcode} through server at {self.url}'}
        
        finally:
            try:
                self.parameter_list[4].set_value("1")
            except Exception as e:
              return {'response':'NOK','error_message':str(e), 'message': f'Failed to run Barcode {Barcode} through server at {self.url}'}
class Arburg(base_server):
    def __init__(self):
        super().__init__()
        self.arburg_counter=0
        self.protocol_counter=0
        self.K1002=self.Param.add_variable(self.namespace,"K1002-Value",ua.Variant(0,ua.VariantType.Int32))
        self.K1002.set_writable()
       
        self.K1003=self.Param.add_variable(self.namespace,"K1003-Value",ua.Variant(0,ua.VariantType.Int32))
        self.K1003.set_writable()
        
        self.K1108=self.Param.add_variable(self.namespace,"K1108-Value",ua.Variant(1,ua.VariantType.Int32))
        self.K1108.set_writable()
        
        self.K1109=self.Param.add_variable(self.namespace,"K1109-Value",ua.Variant(0,ua.VariantType.Int32))
        self.K1109.set_writable()
        
        self.K1110=self.Param.add_variable(self.namespace,"K1110-Value",ua.Variant(0,ua.VariantType.Int32))
        self.K1110.set_writable()
        
        self.S1109=self.Param.add_variable(self.namespace,"S1109-Value",ua.Variant(0,ua.VariantType.Int32))
        
        self.S1109.set_writable()
        self.S1110=self.Param.add_variable(self.namespace,"S1110-Value",ua.Variant(0,ua.VariantType.Int32))
        
        self.S1110.set_writable()
        self.f1450_1=self.Param.add_variable(self.namespace,"f1450.1-Value",ua.Variant(0,ua.VariantType.UInt32))
        self.f1450_1.set_writable()
        
        self.f1450_2=self.Param.add_variable(self.namespace,"f1450.2-Value",ua.Variant(0,ua.VariantType.UInt32))
        self.f1450_2.set_writable()
        
        self.f1450_3=self.Param.add_variable(self.namespace,"f1450.3-Value",ua.Variant(0,ua.VariantType.UInt32))
        self.f1450_3.set_writable()
        
        self.f1450_4=self.Param.add_variable(self.namespace,"f1450.4-Value",ua.Variant(0,ua.VariantType.UInt32))
        self.f1450_4.set_writable()
        
        self.f1450_5=self.Param.add_variable(self.namespace,"f1450.5-Value",ua.Variant(0,ua.VariantType.UInt32))
        self.f1450_5.set_writable()
        
        self.f1450_6=self.Param.add_variable(self.namespace,"f1450.6-Value",ua.Variant(0,ua.VariantType.UInt32))
        self.f1450_6.set_writable()
        
        self.f96352=self.Param.add_variable(self.namespace,"f96352-Value","")
        self.f96352.set_writable()
        self.SetPartID = self.Param.add_method(self.namespace, "SetPartID", self.SetPartID_method, [ua.VariantType.String], [ua.VariantType.Boolean])

        variant_array = [
         ua.Variant(1, ua.VariantType.Int16),
         ua.Variant(25, ua.VariantType.Int16),
         ua.Variant(3.67028, ua.VariantType.Float),
         ua.Variant(1215.05, ua.VariantType.Float),
         ua.Variant("4109283901234, 12093849501234, 1203948124012", ua.VariantType.String),
         ua.Variant(0, ua.VariantType.Int16),
         ua.Variant(0, ua.VariantType.Int16),
         ua.Variant(0, ua.VariantType.Int16)
        ] 


        dv = ua.DataValue(variant_array)

        self.var_array=self.Param.add_variable(self.namespace,"f14007-Last",dv)
        self.var_array.set_writable() 
        self.clear_parameters()
        self.server_thread.start()
        return    
    def SetPartID_method(self,parent,input_value):
        try:
            self.f96352.set_value(input_value)
            return [ua.Variant(True,ua.VariantType.Boolean)]
        except:
            return [ua.Variant(False,ua.VariantType.Boolean)]
    def SetParameterArray(self,error_code=0):
        variant_array=[None,None,None,None,None,None,None,None]
        if(error_code==0):
            variant_array[0]=ua.Variant(1, ua.VariantType.Int16)
            variant_array[7] = ua.Variant(0, ua.VariantType.Int16)
        else:
            variant_array[0]=ua.Variant(0, ua.VariantType.Int16)
            variant_array[7] = ua.Variant(error_code, ua.VariantType.Int16)
        print('Here1')        
        variant_array[1] = ua.Variant(self.arburg_counter, ua.VariantType.Int16)
        print('Here2')  
        self.arburg_counter+=1
        variant_array[2] = ua.Variant(random.randint(0,14), ua.VariantType.Int16)
        print('Here3')  
        variant_array[3] = ua.Variant(0.01, ua.VariantType.Float)
        print('Here4')  
        variant_array[4] = ua.Variant(0.02, ua.VariantType.Float)
        print('Here5')  
        variant_array[5] = ua.Variant(self.protocol_counter, ua.VariantType.Int16)
        print('Here6')  
        self.protocol_counter+=1
        variant_array[6] = ua.Variant(self.f96352.get_value(), ua.VariantType.String)
        print('Here7')  
        updated_data_value = ua.DataValue(variant_array)
        print('Here8')
        print(variant_array)
        print(updated_data_value)
        self.var_array.set_value(updated_data_value)
        print('Here9')
    def clear_parameters(self):
        self.K1002.set_value(None) 
        self.K1003.set_value(None)
        self.K1109.set_value(None)
        self.K1110.set_value(None)
        self.f1450_1.set_value(None)
        self.f1450_2.set_value(None)
        self.f1450_3.set_value(None)
        self.f1450_4.set_value(None)
        self.f1450_5.set_value(None)
        self.f1450_6.set_value(None)
        self.S1109.set_value(0)
        self.S1110.set_value(0)
    def simulate(self,NC_CODE):
        self.clear_parameters()  
        try:
            for step in range(1,7):
                if step==1:
                    self.K1109.set_value(1)
                elif step==2:
                    pass
                elif step==3:
                    while(self.S1109.get_value()!=1 and self.S1110.get_value()!=1):
                        time.sleep(0.3)
                    if(self.S1109.get_value()==1 and self.S1110.get_value()==0):
                        self.K1108.set_value(0)
                    elif(self.S1109.get_value()==0 and self.S1110.get_value()==1):
                        self.clear_parameters()
                        return    
                    
                elif step==4:
                    self.K1110.set_value(1)
                    self.K1109.set_value(0)
                    time.sleep(1)
                elif step==5:
                    self.K1110.set_value(0)
                    self.K1108.set_value(1)
                    if(NC_CODE=="N/A"):
                        self.K1003.set_value(0)
                    else:
                        self.K1003.set_value(1)    
                elif step==6:
                    self.SetParameterArray(NC_CODE)
                
                time.sleep(1)

        except Exception as e:
           return {'response':'NOK','error_message':str(e), 'message': f'Failed to run arburg of code {NC_CODE} through server at {self.url}'}
        
                             