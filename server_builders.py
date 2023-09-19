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
        

        error_codeuri="""
238810
239710
23982
72570
202420
202470
202520
202580
202620
202670
202730
904950
903220
903530
317420
202760
207270
207420
207570
207720
207870
202340
177410
202300
140870
232180
176980
194750
235660
37960
41400
40940
194710
194560
41360
43330
202672
194600
148390
517460
61070
186340
658390
323670
148790
148220
183220
657640
658690
207870
158790
158880
158250
158970
177550
140840
159060
180100
189220
184780
178540
187900
657040
657190
181660
657640
657790
658240
658540
658690
207720
207570
207420
207270
209040
194560
194710
194860
195050
195240
195430
148590
150390
148990
149190
149390
149590
149790
149990
150190
148390
157650
157750
157850
157950
158050
158150
158250
158340
158430
158520
158610
158700
158790
158880
158970
159060
159150
159240
159330
159420
159510
232170
148190
258210
613600
612590
611580
610570
609560
608550
607540
606530
257680
257150
256620
256090
255560
255030
254500
194540
201730
656590
654400
61060
        """
        descrieri="""
Suprainjectare-monitorizare calitate
Suprainjectare-pornire activa
Suprainjectare-buton de pornire activ
Suprainjectare-alarma de manipulare
Suprainjectare-volum comutare
Suprainjectare-presiune de injectie max
Suprainjectare-presiune de comutare
Suprainjectare-timp de injectie
Suprainjectare-start injectie
Suprainjectare-perna de masa/material
Suprainjectare-timp de dozare
Suprainjectare-cuplul de dozare
Suprainjectare-cuplul de dozare mediu
Suprainjectare-dozare munca
Suprainjectare-presiunea medie de inj.
Suprainjectare-timp de injectie variabil
Suprainjectare-zona 1 incalzire cilindru
Suprainjectare-zona 2 incalzire cilindru
N/A
N/A
N/A
Supranjectare-monitorizare pres de inj
Suprainjectare-eroare presiune integrala
Suprainjectare-monitorizare timp maxim de injectie 
Suprainjectare-Timp de ciclu depasit
Suprainjectare-timp asigurare matrita
Suprainjectare-valoare de varf melc
Suprainjectare-debit temperare2mai mica
Suprainjectare-eroare cursa matrita 
Suprainjectare- eroare rupere cablu
Suprainjectare-grila protectie neinchis
Suprainj-Intrerupere bariera optica
Suprainjectare-eroare T856I
Suprainjectare-disp.temp.matrita mica
Suprainjectare-capac protec.vert deschis
Suprainjectare-monitorizare poz.matrita
Suprainj-perna subst.val.reala tol.mica
Suprainjectare-val.debit tol prea mica
Suprainjectare-zona2 incalzire matrita
Suprainjectare-timp pana validare melc
Suprainjectare-oprire de urgenta 3
Suprainjectare-Valoare de varf cav.1.6
Suprainjectare-Valoare de varf cav.1.6.
Suprainjectare-Timp injectie max depasit
Suprainjectare-Circ incalzire matrita 4
Suprainjectare-Tol Circ incalzire mat 1
Suprainjectare-Valoare de varf cav.1.4
Suprainjectare-Valoare de varf cav.3.3
Suprainjectare-Valoare de varf cav.1.8
Suprainjectare-Zona incalzire cilindru 5
Suprainjectare-Disp canal cald zona 13
Suprainjectare-Disp canal cald zona 14
Suprainjectare-Disp canal cald zona 7
Suprainjectare-Disp canal cald zona 15
Suprainjectare-Valoare de varf surub
Suprainjectare-Timp de ciclu
Suprainjectare-Disp canal cald zona 16
Suprainjectare-Valoare de varf cav. 1.2
Suprainjectare-Selectie intrare/iesire
Suprainjectare-Valoare de varf cav. 1.5
Suprainjectare-Valoare de varf cav. 1.1
Suprainjectare-Valoare de varf cav. 1.7
Suprainjectare-Valoare de varf cav. 1.1.
Suprainjectare-Valoare de varf cav. 1.2.
Suprainjectare-Valoare de varf cav. 1.3
Suprainjectare-Valoare de varf cav. 1.3.
Suprainjectare-Valoare de varf cav. 1.4.
Suprainjectare-Valoare de varf cav. 1.5.
Suprainjectare-Valoare de varf cav. 1.7.
Suprainjectare-Valoare de varf cav. 1.8.
Suprainjectare-Zona incalzire cilindru 4
Suprainjectare-Zona incalzire cilindru 3
Suprainjectare-Zona incalzire cilindru 2
Suprainjectare-Zona incalzire cilindru 1
Suprainjectare-Zona incalzire feeder
Suprainjectare-Dispoz temperare matrita 1
Suprainjectare-Dispoz temperare matrita 2
Suprainjectare-Dispoz temperare matrita 3
Suprainjectare-Dispoz temperare matrita 4
Suprainjectare-Dispoz temperare matrita 5
Suprainjectare-Dispoz temperare matrita 6
Suprainjectare-Circ incalzire matrita 3
Suprainjectare-Circ incalzire matrita 12
Suprainjectare-Circ incalzire matrita 5
Suprainjectare-Circ incalzire matrita 6
Suprainjectare-Circ incalzire matrita 7
Suprainjectare-Circ incalzire matrita 8
Suprainjectare-Circ incalzire matrita 9
Suprainjectare-Circ incalzire matrita 10
Suprainjectare-Circ incalzire matrita 11
Suprainjectare-Circ incalzire matrita 2
Suprainjectare-Disp canal cald zona 1
Suprainjectare-Disp canal cald zona 2
Suprainjectare-Disp canal cald zona 3
Suprainjectare-Disp canal cald zona 4
Suprainjectare-Disp canal cald zona 5
Suprainjectare-Disp canal cald zona 6
Suprainjectare-Disp canal cald zona 7
Suprainjectare-Disp canal cald zona 8
Suprainjectare-Disp canal cald zona 9
Suprainjectare-Disp canal cald zona 10
Suprainjectare-Disp canal cald zona 11
Suprainjectare-Disp canal cald zona 12
Suprainjectare-Disp canal cald zona 16
Suprainjectare-Disp canal cald zona 17
Suprainjectare-Disp canal cald zona 18
Suprainjectare-Disp canal cald zona 19
Suprainjectare-Disp canal cald zona 20
Suprainjectare-Disp canal cald zona 21
Suprainjectare-Disp canal cald zona 22
Suprainjectare-Disp canal cald zona 23
Suprainjectare-Disp canal cald zona 24
Suprainjectare-Monitorizare timp protectie matrita
Suprainjectare-Circ incalzire matrita 1
Overmolding-Mould temp control dev 1
None
None
None
None
None
None
None
None
None
None
None
None
None
None
None
None
Suprainjectare-screw volume actual value
        """
        
        dv = ua.DataValue()
        lines1 = error_codeuri.strip().split('\n')
        lines2 = descrieri.strip().split('\n')

        self.NC_DESCRIPTION = {int(key): value for key, value in zip(lines1, lines2)}
        
        self.var_array=self.Param.add_variable(self.namespace,"f14007-Last",dv)
        self.f2072=self.Param.add_variable(self.namespace,"f2072","")
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
        
        
        try:
            
            if(int(error_code)==0):
                cycle_ok=ua.Variant(1, ua.VariantType.Int16)
                cycle_error_code = ua.Variant(0, ua.VariantType.Int32)
                self.f2072.set_value('')
            else:
                cycle_ok=ua.Variant(0, ua.VariantType.Int16)
                cycle_error_code = ua.Variant(int(error_code), ua.VariantType.Int32)
                try:
                    self.f2072.set_value(self.NC_DESCRIPTION[int(error_code)])
                except:
                    self.f2072.set_value('Error description not found')   
            
            cycle_arburg_counter = ua.Variant(self.arburg_counter, ua.VariantType.Int16)
        
            self.arburg_counter+=1
            cycle_param_1 = ua.Variant(random.uniform(0,5), ua.VariantType.Float)
         
            cycle_param_2 = ua.Variant(random.uniform(0,1000), ua.VariantType.Float)
     
            cycle_param_3 = ua.Variant(random.uniform(0,2000), ua.VariantType.Float)
        
            cycle_protocol_counter = ua.Variant(self.protocol_counter, ua.VariantType.Int16)
        
            self.protocol_counter+=1
            f_value=self.f96352.get_value()
            
            cycle_f_value = ua.Variant(f_value, ua.VariantType.String)
            variant_array=[
                cycle_ok,
                cycle_arburg_counter,
                cycle_param_1,
                cycle_param_2,
                cycle_param_3,
                cycle_protocol_counter,
                cycle_f_value,
                cycle_error_code
            ]
            
            dv_1=ua.DataValue(variant_array)
            self.var_array.set_data_value(dv_1)
            
      
        except Exception as e:
            print(f'Failed parameter array update, parameters not written in array, with error : {e}')
       
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
                    self.K1108.set_value(0)
                elif step==3:
                    while(self.S1109.get_value()!=1 and self.S1110.get_value()!=1):
                        time.sleep(0.3)
                    if(self.S1109.get_value()==1 and self.S1110.get_value()==0):
                        pass
                    elif(self.S1109.get_value()==0 and self.S1110.get_value()==1):
                        self.K1003.set_value(1)
                        self.f2072.set_value('Intreruperea ciclului de injectare')
                        return    
                    
                elif step==4:
                    self.K1110.set_value(1)
                    self.K1109.set_value(0)
                    time.sleep(1)
                elif step==5:
                    self.K1110.set_value(0)
                    self.K1108.set_value(1)
                    if(NC_CODE=="0"):
                        self.K1003.set_value(0)
                    else:
                        self.K1003.set_value(1)    
                elif step==6:
                    self.SetParameterArray(NC_CODE)
                
                time.sleep(1)

        except Exception as e:
           return {'response':'NOK','error_message':str(e), 'message': f'Failed to run arburg of code {NC_CODE} through server at {self.url}'}
        
                             