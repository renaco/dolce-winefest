$(document).ready(function(){

    $("#lnk_terminos").click(function(e){
        e.preventDefault();
        //alert("asdasda");
        var url = $(this).attr("href");
        $(".contTerminos").attr("src",url);

        $('.contTerminos').animate({
            opacity: 1,
            left: '0'
        }, 500, function() {
            // Animation complete.
        });

    });

});

