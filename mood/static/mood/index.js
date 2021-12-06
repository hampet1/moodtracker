
// enable submit button after filling out the textarea field
document.addEventListener('DOMContentLoaded', ()=>{
    document.querySelector('#submit').disabled = true;
    document.querySelector('#message').onkeyup = ()=> {
        if(document.querySelector('#message').value.length > 0){
            document.querySelector('#submit').disabled = false;
            }else {
              document.querySelector('#submit').disabled = true;
        }
   }
   });


// show or hide buttons for add and delete medication
document.addEventListener('DOMContentLoaded', ()=> {
  document.querySelectorAll('#form-control-2').forEach((option)=> {
    //onclick handler
    // if you pick add med or del med display pop-up form
    option.onclick = ()=> {
      if(option.value == 'add-medication'){
        //document.getElementById("submit").disabled = false;
        document.getElementById("add-med").hidden = false;
        document.getElementById("del-med").hidden = true;
      }
      if (option.value == 'del-medication'){
        document.getElementById("del-med").hidden = false;
        document.getElementById("add-med").hidden = true;
      }
    }
  });
});


// alert messages
const ALERT_BOX_ADD = document.getElementById("alert-box-add")
