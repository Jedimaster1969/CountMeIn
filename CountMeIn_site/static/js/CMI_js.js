function updateDateAndTime(el,selected_day){

    //function to let site know what date and time a 
    //user selected for their booking

    the_time = el.innerText;
    hour = the_time.slice(0,2);
    minute = the_time.slice(3,5)
                
    if (hour.slice(0,1) == "0" ){
        hour = hour.slice(1,2);
    };

    if (minute.slice(0,1) == "0" ){
        minute = minute.slice(1,2);
    };   

    year = cal.getYear();
    month = cal.getMonth();
    day = selected_day;

    
    $.ajax({
        statusCode:{
            500: function(){
                alert("error with date/time ");
            }
        },
        url: 'update_selected_date_and_time/',
        async: false,
        data:{'year':year, 'month':month, 'day':day, 'hour': hour, 'minute': minute
        },
        dataType:  'json',
        success: function(data){
            if (data.year){
                console.log(data.year + data.month + data.day + data.hour + data.minute);
            }else{
                console.log(data.problem);
            };

        }
                           
    });
  
    
};

function UpdateExceptionDate(el, selected_day, asset_id){

    //function to let site know what date and time a 
    //user selected for their booking

    year = cal.getYear();
    month = cal.getMonth();
    day = selected_day;

    
    $.ajax({
        statusCode:{
            500: function(){
                alert("error with exception date/time ");
            }
        },
        url: 'update_exception_date_and_time/',
        data:{'year':year, 'month':month, 'day':day
        },
        dataType:  'json',
        success: function(data){
            if (data.year){
                console.log(data.year + data.month + data.day);  
                location.href = "/asset/exception/" + asset_id + "/"
            }else{
                console.log(data.problem);
            };

        }
                           
    });



}


function updatePrintButton(el, the_date, the_formatted_date ) {
            
    //the_date format should be YYYYMMDD
    
    console.log("Given date is:" + the_date);
    console.log("Formatted date is:" + the_formatted_date);
    the_year = the_date.slice(0,4);
    the_month = the_date.slice(4,6);
    the_day = the_date.slice(6,8);

    //day and month could have a leading zero so take this out
  
    if (the_month.slice(0,1) == "0" ){
        the_month = the_month.slice(1,2);
    };

    if (the_day.slice(0,1) == "0" ){
        the_day = the_day.slice(1,2);
    };



   document.getElementById("print_link").innerHTML="Print " + the_formatted_date;
   document.getElementById("print_link").href = "../print_bookings/"+the_year+"/" + the_month + "/" + the_day +"/"


};