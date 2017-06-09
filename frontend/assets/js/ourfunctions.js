function sign_up(fname, lname, known, address, age, gender, phone, email, kin_name, kin_relationship, kin_phone){
	var data = "fname="+fname+"&lname="+lname+"&known="+known+"&address="+address+"&age="+age+"&gender="+gender+"&phone="+phone+"&email="+email+"&kin_name="+kin_name+"&kin_relationship"+kin_relationship+"&kin_phone"+kin_phone;

	$.ajax({
	    url : "/forms_wizard",
	    type: "POST",
	    data : data,
	    success: function(data, textStatus, jqXHR)
	    {
	    	if(data['status']==1){
	    		alert("SUCCESS!");
	    	}
	    	else{
	    		alert("Error signing in. Please try again.");
	    	}
	    },
	    error: function (jqXHR, textStatus, errorThrown)
	    {
	 		//Catch error in case we want to show a popup dialog
	    }
	});
}

function load_users(){

}