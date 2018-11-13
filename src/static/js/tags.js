$(function(){ // DOM ready

  // ::: TAGS BOX

  $("#tags input").on({
    focusout : function() {


      if(this.value) {
        console.log($("#tags").text());
        var a = $("#tags").text().indexOf(this.value);
        console.log(a);
        if (a < 0) {
          $("<span/>", {text:this.value.toLowerCase(), insertBefore:this});
          $.ajax({
          	dataType: "json",
            url: "/tags",
          	data: {"new_tag" : this.value, "post_uuid": "False"}, // TODO: FIGURE OUT HOW TO GET THE UUID.
          	success: function(json) {
          	    console.log(json)
          	}
          })
        } else {
          confirm(this.value + " has already been added.");
        }
      }
      this.value = "";
    },
    keyup : function(ev) {
      // if: comma|enter (delimit more keyCodes with | pipe)
      if(/(188|13)/.test(ev.which)) $(this).focusout();
    }
  });
  $('#tags').on('click', 'span', function() {
    if(confirm("Remove "+ $(this).text() +"?")) $(this).remove();
  });

});
