$(document).ready(function() {
	addForm();
	displayCustomField();
	selectListener();
});

var addForm = function() {
	$('.link-formset').formset({
	  addText: 'add form',
	  deleteText: 'remove'
	});
}

var displayCustomField = function(){
	$('.table').on("change", ":checkbox", function() { 
    if (this.checked) {
    	$(this).closest('.custom-box').prevAll().eq(1).addClass("hidden");
    	$(this).closest('.custom-box').prev('.custom-option').removeClass("hidden");
    } else {
    	$(this).closest('.custom-box').prevAll().eq(1).removeClass("hidden");
    	$(this).closest('.custom-box').prev('.custom-option').addClass("hidden");
    }
	});
}

var selectListener = function(){
	$('.table').on('change', '.default-options', function() {
		$(this).closest('.default').next('.custom-option').find(">:first-child").val(this.value)
	})
}
