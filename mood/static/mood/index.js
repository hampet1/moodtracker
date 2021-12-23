
// enable submit button after filling out the textarea field
document.addEventListener('DOMContentLoaded', ()=>{
    document.querySelector('#submit').disabled = true;
    document.querySelector('#submit-med').disabled = true;
    document.querySelector('#message').onkeyup = ()=> {
        if(document.querySelector('#message').value.length > 0){
            document.querySelector('#submit').disabled = false;
            }else {
              document.querySelector('#submit').disabled = true;
        }
   }
   document.querySelector('#med-name').onkeyup = ()=> {
        if(document.querySelector('#med-name').value.length > 0){
            document.querySelector('#submit-med').disabled = false;
            }else {
              document.querySelector('#submit-med').disabled = true;
        }
    }
    document.querySelector('#med-del-name').onkeyup = ()=> {
        if(document.querySelector('#med-del-name').value.length > 0){
            document.querySelector('#delete-med-submit').disabled = false;
            }else {
              document.querySelector('#delete-med-submit').disabled = true;
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



// turning the warning off after 8 second
$(document).ready(function() {
    // show the alert
    setTimeout(function() {
        $("#med-alert").alert('close');
        $("#med-info").alert('close');
        $('#data-processed-info').alert('close');
        $('#med-not-found').alert('close');
        $('#info-posted').alert('close');
    }, 8000);
});




// alert messages
//const ALERT_BOX_ADD = document.getElementById("alert-box-add");
//const ALERT_BOX_DEL = document.getElementById("alert-box-del")


/*
$.ajax({
    type: 'POST',
    url: '',
    data: formData,
    success: function(response){
        console.log(response);
    },
    error: function(error){
        console.log(error);
    }
})

// create a function to handle alerts
*/
