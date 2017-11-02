$(document).ready(function() {
	addForm();
});

var addForm = function() {
	$('.link-formset').formset({
	    addText: '&nbsp;+add form',
	    deleteText: '-remove'
	});
}
