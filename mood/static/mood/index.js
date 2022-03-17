
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

    // checking whether we picked any rating or not
    // without this functionality i would not be able to submit rating regardless the message
    const my_rating = document.querySelector("#rating");
    my_rating.addEventListener('click', ()=>{
        const possible_values = [1,2,3,4,5,6,7,8,9,10];
        var cur_value = parseInt(my_rating.value);
        if(possible_values.includes(cur_value)){
            document.querySelector('#submit').disabled = false;
        }else{
            document.querySelector('#submit').disabled = true;
        }
    });



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
    // close alert after 8000
    setTimeout(function() {
        $("#med-alert").alert('close');
        $("#med-info").alert('close');
        $('#data-processed-info').alert('close');
        $('#med-not-found').alert('close');
        $('#info-posted').alert('close');
        $('#info-posted-2').alert('close');
        $('#info-posted-3').alert('close');
        $('#data-processed-info-rating').alert('close');
        $('#data-processed-info-message').alert('close');
        $('#med-info-error').alert('close');
    }, 8000);
});



// asking user whether to proceed or not even though the medication was not found in the database
document.addEventListener('DOMContentLoaded', ()=> {
    const my_button = document.querySelector('#my-button');

      if (my_button){
          my_button.addEventListener('click', ()=> {

            let confirmation = confirm("would you like to proceed anyway?")
            if (confirmation){
                alert("ahksdkjashdkj");
            }else{
                alert("noo");
           }
      });
    }
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
