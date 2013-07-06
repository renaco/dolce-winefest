$(document).ready(function() {

	//$("#lnk_terminos").colorbox({iframe:true, innerWidth:"691px", innerHeight:"568px"});
	//$(".tyc").colorbox({iframe:true, innerWidth:"691px", innerHeight:"568px"});

	var validator = $("#form_registro").validate({
		rules : {
			first_name : {
				required : true
			},
			last_name : {
				required : true
			},

			dni : {
				required : true,
				minlength : 7
			},
			phone : {
				required : true,
				minlength : 7
			},
			email : {
				required : true,
				email : true
			},
			cod_dpto : {
				required : true
			},
            reply_email : {
                required:true
            },
			tyc : {
				required : true
			}

		},
		messages : {
			first_name : {
				required : "x"
			},
			last_name : {
				required : "x"
			},

			dni : {
				required : "x",
				minlength : "x"
			},
			phone : {
				required : "x",
				minlength : 7
			},
			email : {
				required : "x",
				email : "x"
			},
			cod_dpto : {
				required : "x"
			},
            reply_email : {
                required : "x"
            },
			tyc : {
				required : "x"
			}
		},
		errorPlacement: function(error, element) {
	        error.insertBefore(element)
        },
        highlight: function(element, errorClass, validClass){
            if(element.type == "select-one"){
                $(element).parent().find(".dropdown").addClass("error");
            }
            if(element.type == "checkbox"){
                 $(element).parent().find(".custom").addClass("error");

            }

            $(element).addClass(errorClass).removeClass(validClass);
            $(".validation").css("display","block");
			
        },
        unhighlight: function(element, errorClass, validClass){
            if(element.type == "select-one"){
                $(element).parent().find(".dropdown").removeClass("error");
            }
            if(element.type == "checkbox"){
                $(element).parent().find(".custom").removeClass("error");
            }
            $(element).removeClass(errorClass).addClass(validClass);
        }
	});


    if($("div").hasClass("custom")){
        $('div.custom ul').on('click', 'li', function(event, i) {
            var indexLi = $(this).index();
            var parentLi = $(this).parent().parent().parent().find("select").attr("id");

            $("#" + parentLi + " option").removeAttr('selected');
            $("#" + parentLi + " option:eq("+ indexLi +")").prop('selected',true);

            $("#" + parentLi).change(function(){
                $("#" + parentLi + " option:selected").trigger("click");
            }).trigger('change');
        });
    }

	$(".btn_participar").click(function(e) {
        e.preventDefault();
		if ($("#form_registro").valid() == true) {	
            var url = "user/validator";
            $(".btn_participar").css("display","none");
            $(".btn_participar_off").css("display","block");
            $.ajax({
                type: 'POST',
                url: url,
                data: {dni:$("#numdoc").val(), email:$("#email").val()},
                success: function(html) {

                    if(html == "")
                    {
                        //alert('ola');
                        //var dni = $("#numdoc").val();
                        //_gaq.push(['_trackEvent', 'registro', 'registro',dni ]);
                        document.forms["form_registro"].submit();
                    }else{
                    	var arr = html.split('|');
                        for (var i = 0; i<=(arr.length)-1; i++)
                        {
                            //alert(arr[i]);
                            $("#" + arr[i]).addClass("error");
                        }
                        $(".msj_error div div").css("display","block");
                        $(".msj_error div div").html("Este DNI o correo ya están registrados.");
                    }
                }
            });
		}	
	});

	$('.texto').alpha({allow: " "});
    $('.numero').numeric({ichars:"ñÑ"});

});

// same as email but can validate latam letters
jQuery.validator.addMethod("email", function(value, element, param) {
	return this.optional(element) || /^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.[a-z]{2,5}$/i.test(value);
}, jQuery.validator.messages.email);
