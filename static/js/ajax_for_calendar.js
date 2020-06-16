function updateDateAndTime(el,selected_day){

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