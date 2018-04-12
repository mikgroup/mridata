$(document).ready(function() {
    dataListListener();
});

var dataListListener = function(){
    setTimeout(dataListListener, 10000);

    $.ajax({
	dataType: "json",
	url: "/check_refresh",
	data: "",
	success: function(json) {
	    if (json.refresh) {
		$(".data_list").load(location.href + ".data_list>*","");
	    }
	}
    })
}
