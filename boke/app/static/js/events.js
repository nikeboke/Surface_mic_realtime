const Http = new XMLHttpRequest();

String.prototype.format = function() {
	  a = this;
	  for (k in arguments) {
		      a = a.replace("{" + k + "}", arguments[k])
		    }
	  return a
}

function set_event(obj) {
	const url = "http://127.0.0.1:5000/api/events/setevent"
	const id = obj.getAttribute("event_id")
	if($(obj).is(":checked")){
		var params = "id={0}&active=True".format(id);

	}else{
		var params = "id={0}&active=False".format(id);
	}
	Http.open("GET", url+"?"+params);
	Http.send();
}

function display_event_form(){
	const x = document.getElementsByClassName("create-event-form")[0];
	if(x.style.display === "none"){
		x.style.display = "block";
	}else{
		x.style.display = "none";
	}

}

function save_event(){
	const url = "http://127.0.0.1:5000/api/events/createevent"
	var e = document.getElementById("devices");
	var dev_name = e.options[e.selectedIndex].value;
	var e = document.getElementById("triggers");
	var trig_id = e.options[e.selectedIndex].value;
	var e = document.getElementById("actions");
	var action_id = e.options[e.selectedIndex].value;

	var params = "dev_name={0}&trig_id={1}&action_id={2}".format(dev_name, trig_id, action_id);
	
	Http.open("GET", url+"?"+params);
	Http.send();

	history.go(0);
}

function delete_event(obj){
	const url = "http://127.0.0.1:5000/api/events/deleteevent"
	const id = obj.getAttribute("event_id")
	var params = "id={0}".format(id)
	console.log(params)

	Http.open("GET", url+"?"+params);
	Http.send();

	history.go(0);
}
