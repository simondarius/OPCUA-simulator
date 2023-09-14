
  var socket = io.connect('http://127.0.0.1:5000/');
  var telsonic_table_id=0;
  var adaptronic_table_id=0;
  var tsk_table_id=0;
  let currentActiveView=document.getElementById('adaptronic_content')
  socket.on('connect', function() {
    log_info('Connected to server',1);
  });
  socket.on('message',function(response_data){
    log_info('Response recieved from backend..');
    const response=JSON.parse(response_data);
    flag=response.flag;
    
    switch(flag){
      case 'RefreshInterface':
        target=response.target
        if(target=='Adaptronic'){
        const element_list=document.getElementById('adaptronic_content').querySelector('.simulation_instance_container').querySelectorAll('.simulation_instance')
        if(element_list.length!=response.info.length){
            document.getElementById('adaptronic_content').querySelector('.simulation_instance_container').innerHTML='';
            response.info.forEach(function(url){
              createInstanceDiv(url);
            });
         }
        }else if (target=='Tsk'){
          const element_list=document.getElementById('tsk_content').querySelector('.simulation_instance_container').querySelectorAll('.simulation_instance')
            if(element_list.length!=response.info.length){
            document.getElementById('tsk_content').querySelector('.simulation_instance_container').innerHTML='';
            response.info.forEach(function(url){
              createInstanceDiv(url,target=document.getElementById('tsk_content'));
            });
         }
        }else if (target=='Telsonic'){
          const element_list=document.getElementById('telsonic_content').querySelector('.simulation_instance_container').querySelectorAll('.simulation_instance')
            if(element_list.length!=response.info.length){
            document.getElementById('telsonic_content').querySelector('.simulation_instance_container').innerHTML='';
            response.info.forEach(function(url){
              createInstanceDiv(url,target=document.getElementById('telsonic_content'));
            });
         }
        }else if (target=='Arburg'){
          const element_list=document.getElementById('arburg_content').querySelector('.simulation_instance_container').querySelectorAll('.simulation_instance')
            if(element_list.length!=response.info.length){
            document.getElementById('arburg_content').querySelector('.simulation_instance_container').innerHTML='';
            response.info.forEach(function(url){
              createInstanceDiv(url,target=document.getElementById('arburg_content'));
            });
         }
        }
        break;

      case 'NewInstanceOK':
        createInstanceDiv(response.info,currentActiveView);
        currentActiveView.querySelector('.simulation_new_instance').disabled=false;
        break;
      case 'NewInstanceNOK':
        log_info(`Failed creating new instance: ${response.info}`,2);
        break;
      case 'DeleteInstanceOK':
        index=parseInt(response.index);
        try{
          const parent=currentActiveView.querySelector('.simulation_instance_container')
          const element_list=parent.querySelectorAll('.simulation_instance')
          log_info(index)
          element_list[index].remove()
        
          log_info(`Succesfully removed instance of index ${index}`,1)
        }catch(error){
          log_info(`Unexpected error when deleting div: ${error}`,2)
        }
        break;
      case 'DeleteInstanceNOK':
        log_info(`Failed deleting instance ${response.info}`,2)
        break;
      case 'RunInstanceOK':
        log_info('Successfully ran SFC!',1)
        break;
      case 'RunInstanceNOK':
        log_info(`Failed running : ${response.info}`);
        break;

      default:
        log_info('Unknown response flag is :');
        log_info(response.flag);
        break;
    }
   
                    
  });
  function emitSocketFlag(flag,button){
        type='Unknown'
        if(currentActiveView==document.getElementById('adaptronic_content')){
           type='Adaptronic'
        }else if(currentActiveView==document.getElementById('tsk_content')){
           type='Tsk'
         }else if(currentActiveView==document.getElementById('telsonic_content')){
           type='Telsonic'
         }else if(currentActiveView==document.getElementById('arburg_content')){
          type='Arburg'
        }
        if(flag=='NewInstance'){
          log_info('Started creating new instance....');
          socket.emit('message',JSON.stringify({'flag':'NewInstance','type':type}));
          currentActiveView.querySelector('.simulation_new_instance').disabled=true;
          log_info('Sent request to backend....');
        }
        if(flag=='DeleteInstance'){

          const userConfirmed = confirm("Are you sure you want to delete this instance?");
          if(userConfirmed){
            const parentDiv = button.parentNode;
          
         
            const containerDiv = currentActiveView.querySelector(".simulation_instance_container");
            const divIndex = Array.from(containerDiv.children).indexOf(parentDiv);


            socket.emit('message',JSON.stringify({'flag':'DeleteInstance','index':divIndex,'type':type}));
          }
        }
        if(flag=='RunInstance'){
          log_info('Started request to run data....')
          type='Unknown'
          if(currentActiveView==document.getElementById('adaptronic_content')){
             type='Adaptronic'
          }else if(currentActiveView==document.getElementById('tsk_content')){
             type='Tsk'
           }else if(currentActiveView==document.getElementById('telsonic_content')){
            type='Telsonic'
          }
          try{
          const parentDiv = button.parentNode;
          const selectField = parentDiv.querySelector('.simulation_instance_select');
          const selectedValue = selectField.value;
          
          const contentTable = currentActiveView.querySelector('.content_table');
          const rows = contentTable.getElementsByTagName('tr');
          const containerDiv = currentActiveView.querySelector(".simulation_instance_container");
          const divIndex = Array.from(containerDiv.children).indexOf(parentDiv);
    
          for (let i = 1; i < rows.length; i++) { 
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            
            if (cells[0].textContent === selectedValue) {
              if(type=='Adaptronic'){
              const SFC = cells[1].textContent;
              const NC_CODE = cells[2].textContent;
           
              const Material_Number = cells[3].textContent;
              
              log_info(`Sending SFC ${SFC} to adaptronic server....`)
              socket.emit('message',JSON.stringify({'flag':'RunInstance','index':divIndex,'type':type,'SFC':SFC,'NC_CODE':NC_CODE,'MatNumber':Material_Number}))
              }
              else if(type=='Tsk'){
                const SFC = cells[1].textContent;
                const NC_CODE = cells[2].textContent;
             
                
                
                log_info(`Sending SFC ${SFC} to tsk server....`)
                socket.emit('message',JSON.stringify({'flag':'RunInstance','index':divIndex,'type':type,'SFC':SFC,'NC_CODE':NC_CODE}))
                }
              else if(type=='Telsonic'){
                  const Barcode = cells[1].textContent;
                  const Errorcode = cells[2].textContent;
               
                  
                  
                  log_info(`Sending Barcode ${Barcode} to telsonic server....`)
                  socket.emit('message',JSON.stringify({'flag':'RunInstance','index':divIndex,'type':type,'Barcode':Barcode,'Errorcode':Errorcode}))
                  }  
            }
          }
        }
         catch(error){
          log_info(`Unexpected error when running sfc: ${error}`,2); 
         
          }
      }
        
  }
  document.getElementById("simulation_new_instance_adaptronic").addEventListener("click",()=>{emitSocketFlag('NewInstance');});
  document.getElementById("simulation_new_instance_tsk").addEventListener("click",()=>{emitSocketFlag('NewInstance');});
  document.getElementById("simulation_new_instance_telsonic").addEventListener("click",()=>{emitSocketFlag('NewInstance');});
  document.getElementById("simulation_new_instance_arburg").addEventListener("click",()=>{emitSocketFlag('NewInstance');});
  //Add entry to table 
  
  document.addEventListener("DOMContentLoaded", function () {
    const tsk_content=document.getElementById('tsk_content')
    const adaptronic_content=document.getElementById('adaptronic_content')
    const telsonic_content=document.getElementById('telsonic_content')
    const arburg_content=document.getElementById('arburg_content')
    const submitBtnadaptronic =  document.getElementById("submit_button_adaptronic");
    const submitBtntsk=document.getElementById("submit_button_tsk");
    const header_tsk=document.getElementById('TSK_Header');
    const header_adaptronic=document.getElementById('Adaptronic_Header');
    const header_arburg=document.getElementById('Arburg_Header');
    const randomButtonadaptronic = document.getElementById("random_button_adaptronic");
    const randomButtontsk=document.getElementById("random_button_tsk");
    const submit_button_telsonic = document.getElementById("submit_button_telsonic");
    const random_button_telsonic=document.getElementById("random_button_telsonic");
    const submit_button_arburg = document.getElementById("submit_button_arburg");
    const random_button_arburg=document.getElementById("random_button_arburg");
    const header_telsonic=document.getElementById('Telsonic_Header');
    const logoImage=document.getElementById('logoImage')
    submitBtnadaptronic.addEventListener("click", function () {
      event.preventDefault();
      const dataTable=adaptronic_content.querySelector(".content_table");
      const SFC = adaptronic_content.querySelector(".content_create_input1").value;
      const NC_SELECTOR = adaptronic_content.querySelector(".content_create_input2").value;
      const MAT_NUMBER=adaptronic_content.querySelector(".content_create_input4").value;
      
      if (SFC && NC_SELECTOR && MAT_NUMBER) {
        const newRow = dataTable.insertRow();
        const cell1 = newRow.insertCell(0);
        const cell2 = newRow.insertCell(1);
        const cell3 = newRow.insertCell(2);

        const cell5 = newRow.insertCell(3);
        cell1.innerHTML = adaptronic_table_id;
        cell2.innerHTML = SFC;
        cell3.innerHTML = NC_SELECTOR;
    
        cell5.innerHTML = MAT_NUMBER;
        log_info(`Submited new SFC ${SFC} of id ${adaptronic_table_id}`);
        adaptronic_table_id+=1;
        adaptronic_content.querySelector(".SFC_CREATION_FORM").reset();
        adaptronic_content.querySelector(".content_create_input4").value=MAT_NUMBER;
      }
    });
    submitBtntsk.addEventListener("click", function () {
      event.preventDefault();
      const dataTable=tsk_content.querySelector(".content_table");
      const SFC = tsk_content.querySelector(".content_create_input1").value;
      const NC_SELECTOR = tsk_content.querySelector(".content_create_input2").value;
      if (SFC && NC_SELECTOR) {
        const newRow = dataTable.insertRow();
        const cell1 = newRow.insertCell(0);
        const cell2 = newRow.insertCell(1);
        const cell3 = newRow.insertCell(2);
        cell1.innerHTML = tsk_table_id;
        cell2.innerHTML = SFC;
        cell3.innerHTML = NC_SELECTOR;
        log_info(`Submited new SFC ${SFC} of id ${tsk_table_id}`);
        tsk_table_id+=1;
        tsk_content.querySelector(".SFC_CREATION_FORM").reset();
      }
    });
    submit_button_telsonic.addEventListener("click", function () {
      event.preventDefault();
      const dataTable=telsonic_content.querySelector(".content_table");
      const Barcode = telsonic_content.querySelector(".content_create_input1").value;
      const ErrorCode = telsonic_content.querySelector(".content_create_input2").value;
      if (Barcode && ErrorCode) {
        const newRow = dataTable.insertRow();
        const cell1 = newRow.insertCell(0);
        const cell2 = newRow.insertCell(1);
        const cell3 = newRow.insertCell(2);
        cell1.innerHTML = telsonic_table_id;
        cell2.innerHTML = Barcode;
        cell3.innerHTML = ErrorCode;
        log_info(`Submited new Barcode ${Barcode} of id ${telsonic_table_id}`);
        telsonic_table_id+=1;
        telsonic_content.querySelector(".SFC_CREATION_FORM").reset();
      }
    });
    submit_button_arburg.addEventListener("click", function () {
      event.preventDefault();
      const dataTable=telsonic_content.querySelector(".content_table");
      const Barcode = telsonic_content.querySelector(".content_create_input1").value;
      const ErrorCode = telsonic_content.querySelector(".content_create_input2").value;
      if (Barcode && ErrorCode) {
        const newRow = dataTable.insertRow();
        const cell1 = newRow.insertCell(0);
        const cell2 = newRow.insertCell(1);
        const cell3 = newRow.insertCell(2);
        cell1.innerHTML = telsonic_table_id;
        cell2.innerHTML = Barcode;
        cell3.innerHTML = ErrorCode;
        log_info(`Submited new Barcode ${Barcode} of id ${telsonic_table_id}`);
        telsonic_table_id+=1;
        telsonic_content.querySelector(".SFC_CREATION_FORM").reset();
      }
    });
    header_tsk.addEventListener('click',function(){
      event.preventDefault();
      
      log_info('TSK_Clicked',2);
    
      switch(currentActiveView){
        case document.getElementById('adaptronic_content'):
          changeGradientAsync('rgba(96,119,166,1)','rgba(147,42,42,1)')
          break;
        case document.getElementById('telsonic_content'):
          changeGradientAsync('rgba(119,147,42,1)','rgba(147,42,42,1)')
          break;
        case document.getElementById('arburg_content'):
          changeGradientAsync('rgba(126,223,210,1)','rgba(147,42,42,1)')
          break;    
        default:
          break;     
      }
      anime({
        targets:[currentActiveView],
        top:['120%'],
        opacity:0,
        duration:700,
        easing:'linear',
        complete:function(){
          logoImage.src=window.red_logo_url;
          anime({
            targets:["#tsk_content"],
            top:["10%"],
            opacity:1,
            duration:700,
            easing:'linear',
            complete:function(){
               anime({
                targets:'.header_menu',
                color:"#932A2A",
                duration:200,
                easing:'linear',
               })
            }
          })
        }
      })
       currentActiveView=document.getElementById('tsk_content');

    })
    header_telsonic.addEventListener('click',function(){
      event.preventDefault();
      
      log_info('Telsonic_Clicked',2);
      switch(currentActiveView){
        case document.getElementById('adaptronic_content'):
          changeGradientAsync('rgba(96,119,166,1)','rgba(119,147,42,1)')
          break;
        case document.getElementById('tsk_content'):
          changeGradientAsync('rgba(147,42,42,1)','rgba(119,147,42,1)')
          break;
        case document.getElementById('arburg_content'):
          changeGradientAsync('rgba(126,223,210,1)','rgba(119,147,42,1)')
          break;  
        default:
          break;     
      }
      anime({
        targets:[currentActiveView],
        top:['120%'],
        opacity:0,
        duration:700,
        easing:'linear',
        complete:function(){
          logoImage.src=window.green_logo_url;
          anime({
            targets:["#telsonic_content"],
            top:["10%"],
            opacity:1,
            duration:700,
            easing:'linear',
            complete:function(){
               anime({
                targets:'.header_menu',
                color:"#82944f",
                duration:200,
                easing:'linear',
               })
            }
          })
        }
      })
       currentActiveView=document.getElementById('telsonic_content');

    })
    header_adaptronic.addEventListener('click',function(){
      event.preventDefault();
      log_info('Adaptronic Clicked!',2);
      switch(currentActiveView){
        case document.getElementById('telsonic_content'):
          changeGradientAsync('rgba(119,147,42,1)','rgba(96,119,166,1)')
          break;
        case document.getElementById('tsk_content'):
          changeGradientAsync('rgba(147,42,42,1)','rgba(96,119,166,1)')
          break;
        case document.getElementById('arburg_content'):
          changeGradientAsync('rgba(126,223,210,1)','rgba(96,119,166,1)')
          break;
        default:
          break;     
      }
      anime({
        targets:currentActiveView,
        top:'120%',
        opacity:0,
        duration:700,
        easing:'linear',
        complete:function(){
          logoImage.src=window.blue_logo_url
          anime({
            targets:"#adaptronic_content",
            top:"10%",
            opacity:1,
            duration:700,
            easing:'linear',
            complete:function(){
              anime({
              targets:'.header_menu',
              color:"#575759",
              duration:200,
              easing:'linear',
            })
            }
          })
        }
      })
       currentActiveView=document.getElementById('adaptronic_content');
    })
    header_arburg.addEventListener('click',function(){
      event.preventDefault();
      log_info('Arburg Clicked!',2);
      switch(currentActiveView){
        case document.getElementById('telsonic_content'):
          changeGradientAsync('rgba(119,147,42,1)','rgba(126,223,210,1)')
          break;
        case document.getElementById('tsk_content'):
          changeGradientAsync('rgba(147,42,42,1)','rgba(126,223,210,1)')
          break;
        case document.getElementById('adaptronic_content'):
          changeGradientAsync('rgba(96,119,166,1)','rgba(126,223,210,1)')
          break;  
        default:
          break;     
      }
      anime({
        targets:currentActiveView,
        top:'120%',
        opacity:0,
        duration:700,
        easing:'linear',
        complete:function(){
          logoImage.src=window.light_logo_url
          anime({
            targets:"#arburg_content",
            top:"10%",
            opacity:1,
            duration:700,
            easing:'linear',
            complete:function(){
              anime({
              targets:'.header_menu',
              color:"#57827b",
              duration:200,
              easing:'linear',
            })
            }
          })
        }
      })
       currentActiveView=document.getElementById('arburg_content');
    })
     randomButtonadaptronic.addEventListener("click", function () {
      event.preventDefault();
      
      const sfcInput=adaptronic_content.querySelector(".content_create_input1");
      const ncCodeSelect=adaptronic_content.querySelector(".content_create_input2");
      const randomSFC = Math.floor(Math.random() * 9000000000000) + 1000000000000;
      sfcInput.value = randomSFC;
  
      
      const randomOptionIndex = Math.floor(Math.random() * ncCodeSelect.options.length);
      ncCodeSelect.selectedIndex = randomOptionIndex;
    });
    randomButtontsk.addEventListener("click", function () {
      event.preventDefault();
      const sfcInput=tsk_content.querySelector(".content_create_input1");
      const ncCodeSelect=tsk_content.querySelector(".content_create_input2");
      const randomSFC = Math.floor(Math.random() * 9000000000000) + 1000000000000;
      sfcInput.value = randomSFC;
  
      
      const randomOptionIndex = Math.floor(Math.random() * ncCodeSelect.options.length);
      ncCodeSelect.selectedIndex = randomOptionIndex;
    });
    random_button_telsonic.addEventListener("click", function () {
      event.preventDefault();
      const sfcInput=telsonic_content.querySelector(".content_create_input1");
      const ncCodeSelect=telsonic_content.querySelector(".content_create_input2");
      const randomSFC = Math.floor(Math.random() * 9000000000000) + 1000000000000;
      sfcInput.value = randomSFC;
  
      
      const randomOptionIndex = Math.floor(Math.random() * ncCodeSelect.options.length);
      ncCodeSelect.selectedIndex = randomOptionIndex;
    });
    random_button_arburg.addEventListener("click", function () {
      event.preventDefault();
      const sfcInput=telsonic_content.querySelector(".content_create_input1");
      const ncCodeSelect=telsonic_content.querySelector(".content_create_input2");
      const randomSFC = Math.floor(Math.random() * 9000000000000) + 1000000000000;
      sfcInput.value = randomSFC;
  
      
      const randomOptionIndex = Math.floor(Math.random() * ncCodeSelect.options.length);
      ncCodeSelect.selectedIndex = randomOptionIndex;
    });
    
  });
  
  
 
  
  function createInstanceDiv(url='Unknown',target=document.getElementById('adaptronic_content')){
  
    const containerDiv = target.querySelector(".simulation_instance_container");
                          
  
    const newDiv = document.createElement("div");
    newDiv.classList.add("simulation_instance"); 


    const label = document.createElement("label");
    label.textContent = "SFC:";

    const select = document.createElement("select");
    select.classList.add("simulation_instance_select");
    select.id = "simulation_instance_select";
    const tableElement = target.querySelector(".content_table");


     for (const row of tableElement.rows) {

     const id = row.cells[0].textContent;
     if(id=='ID')continue;

     const option = document.createElement("option");
     option.value = id;
     option.textContent = id;
     select.appendChild(option);
    }

    const buttonRun = document.createElement("button");
    buttonRun.classList.add("simulation_instance_run");
    buttonRun.id = "simulation_instance_run";
    buttonRun.textContent = "Run";
    buttonRun.addEventListener("click", ()=> {
           emitSocketFlag('RunInstance',event.target);
     })
    const info = document.createElement("h5");
    info.classList.add("simulation_instance_info");
    info.textContent = "SERVER RUNNING AT: "+url;

    const buttonDelete = document.createElement("button");
    buttonDelete.classList.add("simulation_instance_delete");
    buttonDelete.id = "simulation_instance_delete";
    buttonDelete.textContent = "Delete";
    buttonDelete.addEventListener("click", () => {
           emitSocketFlag('DeleteInstance',event.target);
     });


    newDiv.appendChild(label);
    newDiv.appendChild(select);
    newDiv.appendChild(buttonRun);
    newDiv.appendChild(info);
    newDiv.appendChild(buttonDelete);


    containerDiv.appendChild(newDiv);
    log_info("Created instance!",1);
  }
  function log_info(to_log,color_code=0){
    const currentDate=new Date()
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth() 
    const day = currentDate.getDate();
    const hours = currentDate.getHours();
    const minutes = currentDate.getMinutes();
    const seconds = currentDate.getSeconds();
    new_log=document.createElement('h4');
    new_log.textContent=`${year}.${month}.${day}-`+`${hours}:${minutes}:${seconds}  `+to_log;
    if(color_code==1)new_log.style.color='green';
    if(color_code==2)new_log.style.color='red';
    console=currentActiveView.querySelector('.simulation_console')
    console.appendChild(new_log);
  }
  
  
  // Function to update options in a select element based on data in the content table
 //Observer
 function updateSelectElements(type) {
  if(type=='Adaptronic')return document.getElementById('adaptronic_content').querySelectorAll(".simulation_instance_select");
  if(type=='Tsk')return document.getElementById('tsk_content').querySelectorAll(".simulation_instance_select");
  if(type=='Telsonic')return document.getElementById('telsonic_content').querySelectorAll(".simulation_instance_select");
}

// Initial NodeList
const observer_adaptronic = new MutationObserver((mutationsList, observer) => {
  for (const mutation of mutationsList) {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      
      mutation.addedNodes.forEach(addedNode => {
     
        const id = addedNode.cells[0].textContent;
        selectElements = updateSelectElements('Adaptronic');
       
        selectElements.forEach(selectElement => {
          const option = document.createElement("option");
          option.value = id;
          option.textContent = id;
          selectElement.appendChild(option);
        });
      });
    }
  }
});


const config_adaptronic = { childList: true, subtree: true };


observer_adaptronic.observe(document.getElementById('adaptronic_content').querySelector('.content_table'), config_adaptronic);
const observer_tsk = new MutationObserver((mutationsList, observer) => {
  for (const mutation of mutationsList) {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      
      mutation.addedNodes.forEach(addedNode => {
     
        const id = addedNode.cells[0].textContent;
        selectElements = updateSelectElements('Tsk');
       
        selectElements.forEach(selectElement => {
          const option = document.createElement("option");
          option.value = id;
          option.textContent = id;
          selectElement.appendChild(option);
        });
      });
    }
  }
});


const config_tsk = { childList: true, subtree: true };


observer_tsk.observe(document.getElementById('tsk_content').querySelector('.content_table'), config_tsk);

const observer_telsonic = new MutationObserver((mutationsList, observer) => {
  for (const mutation of mutationsList) {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      
      mutation.addedNodes.forEach(addedNode => {
     
        const id = addedNode.cells[0].textContent;
        selectElements = updateSelectElements('Telsonic');
       
        selectElements.forEach(selectElement => {
          const option = document.createElement("option");
          option.value = id;
          option.textContent = id;
          selectElement.appendChild(option);
        });
      });
    }
  }
});


const config_telsonic = { childList: true, subtree: true };


observer_telsonic.observe(document.getElementById('telsonic_content').querySelector('.content_table'), config_telsonic);

async function changeGradientAsync(from,to) {
  const rootElement = document.querySelector('.root');
  if (!rootElement) {
    console.error('Element with class "root" not found.');
    return;
  }


  for (let delta = 0; delta <= 100; delta++) {
    rootElement.style.background = `linear-gradient(180deg, rgba(255,255,255,1) ${delta}%, ${from} 100%)`;
    await new Promise(resolve => setTimeout(resolve, 5)); 
  }
  rootElement.style.background='linear-gradient(180deg, rgba(255,255,255,1) 99%, rgba(96,119,166,1) 100%);'
  for (let delta = 99; delta >= 0; delta--) {
    rootElement.style.background = `linear-gradient(180deg, rgba(255,255,255,1) ${delta}%, ${to} 100%)`;
    await new Promise(resolve => setTimeout(resolve, 5)); 
  }
}
