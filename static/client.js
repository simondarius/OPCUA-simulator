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
    console=document.getElementById("log_console");
    console.appendChild(new_log);
  }
  
  log_info("Started Application!")
  
  
  //Code to block selecting OK MII STATUS when simulated NC_CODE contradicts it
  const ncCodeSelect = document.getElementById('content_create_input2');
  const miiStatusSelect = document.getElementById('content_create_input3');
  
  ncCodeSelect.addEventListener('change', () => {
    const selectedValue = ncCodeSelect.value;
    
    if (selectedValue === '5' || selectedValue === '6' || selectedValue === '7') {
      miiStatusSelect.value = 'NOK';
      for (const option of miiStatusSelect.options) {
        if (option.value === 'OK') {
          option.disabled = true;
        } else {
          option.disabled = false;
        }
      }
    } else {
      for (const option of miiStatusSelect.options) {
        option.disabled = false;
      }
    }
  });
  
  
  //Add entry to table 
  let id=0;
  document.addEventListener("DOMContentLoaded", function () {
    const submitBtn = document.getElementById("submit_button");
    const dataTable = document.getElementById("content_table");
  
    submitBtn.addEventListener("click", function () {
      event.preventDefault();
      const SFC = document.getElementById("content_create_input1").value;
      const NC_SELECTOR = document.getElementById("content_create_input2").value;
      const MII_SELECTOR = document.getElementById("content_create_input3").value
      const MAT_NUMBER=document.getElementById("content_create_input4").value;
      if (SFC && NC_SELECTOR && MII_SELECTOR) {
        const newRow = dataTable.insertRow();
        const cell1 = newRow.insertCell(0);
        const cell2 = newRow.insertCell(1);
        const cell3 = newRow.insertCell(2);
        const cell4 = newRow.insertCell(3);
        const cell5 = newRow.insertCell(4);
        cell1.innerHTML = id;
        cell2.innerHTML = SFC;
        cell3.innerHTML = NC_SELECTOR;
        cell4.innerHTML = MII_SELECTOR;
        cell5.innerHTML = MAT_NUMBER;
        log_info(`Submited new SFC ${SFC} of id ${id}`);
        id+=1;
        document.getElementById("SFC_CREATION_FORM").reset();
      }
    });
  });
  //Delete instance from server
  function confirmAndDelete(button) {
  
      const userConfirmed = confirm("Are you sure you want to delete this instance?");
      
      if (userConfirmed) {
         
          const parentDiv = button.parentNode;
          
         
          const containerDiv = document.getElementById("simulation_instance_container");
          const divIndex = Array.from(containerDiv.children).indexOf(parentDiv);
          
         
          fetch("http://localhost:5000/Delete_Instance", {
              method: 'POST',
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ "to_delete": divIndex })
          })
          .then(response => response.json())
          .then(data => {
              if (data['response'] === 'OK') {
                  
                  parentDiv.remove();
                  log_info("Removed Instance with success",1)
              } else {
                log_info("Deletion failed, message:" + data['message'],2);
              }
          })
          .catch(error => {
              log_info("Unknown error during deletion:" + error.message,2);
          });
      }
  }
  //Run data to opcua server for simulation
  function runData(button) {
  
        log_info('Started request to run data....')
           
        try{
        const parentDiv = button.parentNode;
        const selectField = parentDiv.querySelector('.simulation_instance_select');
        const selectedValue = selectField.value;
        
        const contentTable = document.getElementById('content_table');
        const rows = contentTable.getElementsByTagName('tr');
        const containerDiv = document.getElementById("simulation_instance_container");
        const divIndex = Array.from(containerDiv.children).indexOf(parentDiv);
  
        for (let i = 1; i < rows.length; i++) { 
          const row = rows[i];
          const cells = row.getElementsByTagName('td');
          
          if (cells[0].textContent === selectedValue) {
            const SFC = cells[1].textContent;
            const NC_CODE = cells[2].textContent;
            const MII_STATUS = cells[3].textContent;
            const Material_Number = cells[4].textContent;
            
            log_info(`Sending SFC ${SFC} to server....`)
            fetch('http://localhost:5000/Run_Instance', {
              method: 'POST', 
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                'SFC': SFC,
                'NC_CODE': NC_CODE,
                'MII_STATUS': MII_STATUS,
                'Material_Number': Material_Number,
                'to_update':divIndex
              })
            })
            .then(response => response.json())
            .then(data => {
              
               if(data['response']=='OK'){
                log_info(data['message'],1);
                
               }
               else{
               
                log_info(data['error_message'],2);
               }
  
            })
            .catch(error => {
                log_info(error,2);
                
            });
            
            break; 
          }
          
        }
      }catch(error){
        log_info(`Unknown error when running sfc: ${error}`,2); 
       
      }
  }
  
  //Random button code
  document.addEventListener("DOMContentLoaded", function () {
    const randomButton = document.getElementById("random_button");
    const sfcInput = document.getElementById("content_create_input1");
    const ncCodeSelect = document.getElementById("content_create_input2");
    const miiStatusSelect = document.getElementById("content_create_input3");
  
    randomButton.addEventListener("click", function () {
      event.preventDefault();
      
      const randomSFC = Math.floor(Math.random() * 9000000000000) + 1000000000000;
      sfcInput.value = randomSFC;
  
      
      const randomOptionIndex = Math.floor(Math.random() * ncCodeSelect.options.length);
      ncCodeSelect.selectedIndex = randomOptionIndex;
  
      
      const randomStatusIndex = Math.floor(Math.random() * miiStatusSelect.options.length);
      miiStatusSelect.selectedIndex = randomStatusIndex;
    });
  });
  //Instance creation logic
  document.addEventListener("DOMContentLoaded",function(){
    const CreateInstance=document.getElementById("simulation_new_instance");
    CreateInstance.addEventListener("click",function(){
          log_info("Started new instance creation....");
          fetch("http://localhost:5000/New_Instance",
                {method:'POST',headers: {"Content-Type":"application/json"},body:JSON.stringify({'request':'CreateNewInstance'})}       
          ).then(response=>response.json()).then(response=>{
                      if(response['response']=='OK'){
                          
                          const containerDiv = document.getElementById("simulation_instance_container");
                          
  
                          const newDiv = document.createElement("div");
                          newDiv.classList.add("simulation_instance"); 
  
  
                          const label = document.createElement("label");
                          label.textContent = "SFC:";
  
                          const select = document.createElement("select");
                          select.classList.add("simulation_instance_select");
                          select.id = "simulation_instance_select";
                          const tableElement = document.getElementById("content_table");
  
  
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
                          buttonRun.addEventListener("click", function() {
                                 runData(this); 
                           })
                          const info = document.createElement("h5");
                          info.classList.add("simulation_instance_info");
                          info.textContent = "SERVER RUNNING AT: "+response['server_url'];
  
                          const buttonDelete = document.createElement("button");
                          buttonDelete.classList.add("simulation_instance_delete");
                          buttonDelete.id = "simulation_instance_delete";
                          buttonDelete.textContent = "Delete";
                          buttonDelete.addEventListener("click", function() {
                                 confirmAndDelete(this); 
                           });
  
  
                          newDiv.appendChild(label);
                          newDiv.appendChild(select);
                          newDiv.appendChild(buttonRun);
                          newDiv.appendChild(info);
                          newDiv.appendChild(buttonDelete);
  
  
                          containerDiv.appendChild(newDiv);
                          log_info("Created instance!",1);
                          }else{
                            log_info(`Failed creating new instance, response from server: ${response['response']} error : ${response['error_message']}`,2);
  
                          }
                }).catch(error => {
                  log_info(`Unknown error in instance creation request: ${error}`,2);
  
                })
                
              });
  })
  //Observer
  function updateSelectElements() {
    return document.querySelectorAll(".simulation_instance_select");
  }
  
  // Initial NodeList
  let selectElements = updateSelectElements();
  const tableElement = document.getElementById("content_table");
  
  
  
  const observer = new MutationObserver((mutationsList, observer) => {
    for (const mutation of mutationsList) {
      if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
        
        mutation.addedNodes.forEach(addedNode => {
       
          const id = addedNode.cells[0].textContent;
          selectElements = updateSelectElements();
         
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
  
  
  const config = { childList: true, subtree: true };
  
  
  observer.observe(tableElement, config);
  
  
  