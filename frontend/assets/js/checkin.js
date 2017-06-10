function check_in(){
	var email = $("#email").val();
	console.log(email);
	var arnumber = $("#arnumber").val(); 
	var data = "email="+email+"&arnumber="+arnumber;
	console.log(data);
	$.ajax({
	    url : "/checkin",
	    type: "POST",
	    data : data,
	    success: function(data, textStatus, jqXHR)
	    {
	    	if(data['status']==1){
	    		alert("SUCCESS!");
	    	}
	    	else{
	    		alert("Error checking in. Please try again.");
	    	}
	    },
	    error: function (jqXHR, textStatus, errorThrown)
	    {
	 		//Catch error in case we want to show a popup dialog
	    }
	});
}

function check_out(){
	var email = $("#email").val();
	console.log(email);
	var data = "email="+email;
	console.log(data);
	$.ajax({
	    url : "/checkin",
	    type: "POST",
	    data : data,
	    success: function(data, textStatus, jqXHR)
	    {
	    	if(data['status']==1){
	    		alert("SUCCESS!");
	    	}
	    	else{
	    		alert("Error checking in. Please try again.");
	    	}
	    },
	    error: function (jqXHR, textStatus, errorThrown)
	    {
	 		//Catch error in case we want to show a popup dialog
	    }
	});
}