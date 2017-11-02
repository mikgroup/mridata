$(document).ready(function() {
	termsModalListener();
});

var termsModalListener = function() {
	var modal = $('.terms-modal');
	
	$('.terms').on("click", function(){
		modal.removeClass("hidden")
	});

	$('.terms-modal-close').on("click", function(){
		modal.addClass("hidden")
	}); 
}