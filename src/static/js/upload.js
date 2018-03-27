$(document).ready(function() {
    toggleCustomField();
    selectListener();
    termsModalListener();
});

var toggleCustomField = function(){
    $('#custom-checkbox').click(function() {
	$("#default-options").toggle(!this.checked);
	$("#custom-option").toggle(this.checked);
    });
}

var selectListener = function(){
    $('#default-options-select').change(function() {
	$('#id_anatomy').val(this.value)
    })
}

var termsModalListener = function() {
    var modal = $('.terms-modal');
    
    $('.terms').on("click", function(){
	modal.removeClass("hidden")
    });

    $('.terms-modal-close').on("click", function(){
	modal.addClass("hidden")
    }); 
}
