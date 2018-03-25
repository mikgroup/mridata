$(document).ready(function() {
    dataListListener();
});

var dataListListener = function(){
    setTimeout(dataListListener, 1000);
    $.get('pagelink.php', function(data) {
        $('#content_div_id').html(data);    
    });
}
