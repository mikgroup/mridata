$(document).ready(function() {
    toggleCustomField();
    selectListener();
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
