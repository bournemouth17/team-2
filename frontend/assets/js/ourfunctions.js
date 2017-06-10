function sign_up(fname, lname, known, address, age, gender, phone, email, kin_name, kin_relationship, kin_phone, outdoor, indoor, interests){
	var data = "fname="+fname+"&lname="+lname+"&known="+known+"&address="+address
			+"&age="+age+"&gender="+gender+"&phone="+phone+"&email="+email
			+"&kin_name="+kin_name+"&kin_relationship="+kin_relationship+"&kin_phone="+kin_phone
			+"&outdoor="+outdoor+"&indoor="+indoor+"&interests="+interests;

	console.log(data);

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

function load_user(){
	email_add = $("#email").val();
	data = "email="+email_add;

	console.log("REACHED HERE!");

	$.ajax({
	    url : "/userinfo",
	    type: "POST",
	    data : data,
	    success: function(data, textStatus, jqXHR)
	    {
	    	console.log(data);
	    	if(data['status']==1){
	    		//Load details into the page

	    		$("#user_edit_name").html(data['user'].fname+" "+data["user"].lname);
	    		$("#user_edit_address").html(data['user'].address);
	    		$("#edit_fname").val(data['user'].fname);
	    		$("#edit_lname").val(data['user'].lname);
	    		$("#edit_address").val(data['user'].address);
	    		$("#edit_age").val(data['user'].age);
	    		$("#edit_email").val(data['user'].email);
	    		$("#edit_phone").val(data['user'].phone);
	    		$("#edit_known").val(data['user'].known);
	    		$("#edit_kin_name").val(data['user'].kin_name);
	    		$("#edit_kin_relationship").val(data['user'].kin_relationship);
	    		

	    		//Show the div now
	    		$("#userinformation").show();
	    	}
	    	else{
	    		alert("Error signing in. Please try again.");
	    	}
	    },
	    error: function (jqXHR, textStatus, errorThrown)
	    {
	 		//Catch error in case we want to show a popup dialog
	 		alert("Error signing in. Please try again.");
	    }
	});
}

function edit_user(){
	//Capture data
    fname = $("#edit_fname").val();
    lname = $("#edit_lname").val();
    known = $("#edit_known").val();
    address = $("#edit_address").val();
    age = $("#edit_age").val();
    gender = $("#edit_gender").val();
    phone = $("#edit_phone").val();
    email = $("#edit_email").val();
    kin_name = $("#edit_kin_name").val();
    kin_relationship = $("#edit_kin_relationship").val();
    kin_phone = $("#edit_kin_phone").val();
    interests = $("#edit_interests").val();

    var data = "fname="+fname+"&lname="+lname+"&known="+known+"&address="+address
			+"&age="+age+"&gender="+gender+"&phone="+phone+"&email="+email
			+"&kin_name="+kin_name+"&kin_relationship="+kin_relationship+"&kin_phone="+kin_phone
			+"&outdoor="+outdoor+"&indoor="+indoor+"&interests="+interests;

	console.log(data);

	$.ajax({
	    url : "/forms_wizard",
	    type: "PUT",
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

