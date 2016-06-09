$('.date-format').datepicker({
	todayBtn: 'linked',
	keyboardNavigation: false,
	forceParse: false,
	calendarWeeks: true,
	autoclose: true,
	format: 'dd/mm/yyyy',
});

$(".file-format").filestyle({
	placeholder: "Seleccionar Archivo",
	buttonText: ""
});


var language = {
	'emptyTable': 'Sin Datos',
	// 'info': '_START_-_END_ de _TOTAL_ ',
	'info': 'mostranto _END_ de _TOTAL_ registros',
	'infoEmpty': '0-0 de 0',
	'infoFiltered': '',
	'infoPostFix': '',
	'thousands': ',',
	'lengthMenu': '_MENU_',
	// 'lengthMenu': 'Mostrar _MENU_ items',
	'loadingRecords': 'Cargando...',
	'processing': 'Procesando...',
	'search': '',
	'searchPlaceholder': 'Buscar',
	'zeroRecords': 'No se encontraron registros',
	'paginate': {
		'first': 'Primero',
		'last': 'Último',
		'next': 'Próximo',
		'previous': 'Anterior'
	}
}

$(".select2").select2();

$('[data-toggle="tooltip"]').tooltip()

function getCookie(name){
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function apply_errors_form(errors){
	$.each(errors, function(index, value) {
		if (index === "__all__") {
			django_message(value[0], "error");
		} else {
			var input = $("#id_" + index),
			container = $("#div_id_" + index),
			error_msg = $("<li /> ").addClass("errorlist").text(value[0]);
			$("#id_" + index).parent().find('.container-error').append(error_msg)
		}
	});
}

function clear_errors_form(form){
	$(form +' '+ '.container-error').html('')
}

function clear_form(form){
	$(form +' '+ '.form-group input').val('')
	$(form +' '+ '.form-group textarea').val('')
	$(form +' '+ 'select option:first-child').prop('selected', true);
}

function search_column_table(obj, table_entidad){
	value = $(obj).val()
	index = $(obj).attr('data-column')
	$(table_entidad).DataTable().column(index).search(value).draw()
}

function notification_toast(toast_type, toast_title, toast_text){
	toastr.options = {
		"closeButton": true,
		"debug": false,
		"progressBar": true,
		"preventDuplicates": false,
		"positionClass": "toast-top-right",
		"onclick": null,
		"showDuration": "400",
		"hideDuration": "1000",
		"timeOut": "3000",
		"extendedTimeOut": "1000",
		"showEasing": "swing",
		"hideEasing": "linear",
		"showMethod": "fadeIn",
		"hideMethod": "fadeOut"
	}

	toastr[toast_type](toast_text, toast_title)
}


function load_table(tabla_id, columnas, configuracion){

	var buttons = [
	{
		extend: 'excel'
	},
	{
		extend: 'pdf'
	},
	{
		extend: 'print',
		customize: function (win){
			$(win.document.body).addClass('white-bg');
			$(win.document.body).css('font-size', '10px');
			$(win.document.body).find('table').addClass('compact').css('font-size', 'inherit');
		}
	}]

	var tabla = $(tabla_id).DataTable({
		'language': language,
		'pageLength': 10,
		'searching': configuracion.searching == null ? true : configuracion.searching,
		'order': configuracion.order == null ? [[0, 'desc']] : configuracion.order,
		'paginate':  configuracion.paginate == null  ? true : configuracion.paginate,
		'bLengthChange': configuracion.bLengthChange == null  ? true : configuracion.bLengthChange,
		'bInfo': configuracion.bInfo == null  ? true : configuracion.bInfo,
		'pagingType': 'simple_numbers',
		'columns': columnas,
		'dom': '<"top">fl<"html5buttons"B>rt <"bottom"ip><"clear">',
		'buttons': configuracion.buttons == null  ? buttons : configuracion.buttons,

	});

	return tabla;
}


function open_modal_delete(obj, id, model, tabla, text){


	var col = $(obj).closest('tr')
	swal({
		title: '¿ Eliminar '+text+' ?',
		text: '',
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#F68793',
		confirmButtonText: 'Si, eliminar',
		cancelButtonText: 'Cancelar',
		closeOnConfirm: true 
	}, function(){

		$.ajax({
			url: '/'+model+'/delete/'+id,
			type: 'POST',
			data: {csrfmiddlewaretoken: getCookie('csrftoken')},
			success: function(data){
				var table = $('#'+tabla).DataTable();
				table.row($(col)).remove().draw();
				notification_toast('success', 'Exito', 'eliminado correctamente')
			},
			error:function(data){
				notification_toast('error', 'Error', 'no se puedo eliminar')
			}
		})
	});
}


function open_modal_delete_child(obj, text){

	swal({
		title: '¿ Eliminar '+text+' ?',
		text: '',
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#F68793',
		confirmButtonText: 'Si, eliminar',
		cancelButtonText: 'Cancelar',
		closeOnConfirm: true 
	}, function(){
		$(obj).closest('tr').find('input:checkbox:last').prop('checked', true)
		$(obj).closest('tr').addClass('hide')
	});	
}


function guardar_formulario(accion, form){

	$.ajax({
		type: 'post',
		url: $('#'+form).attr('action'),
		data: $('#'+form).serialize(),
		success: function(response) {
			if (accion == 'create') {
				clear_form('#'+form)
			}
			clear_errors_form('#'+form)

			notification_toast('success', 'ÉXITO', 'guardado correctamente')
		},
		error: function(data, textStatus, jqXHR) {
			clear_errors_form('#'+form)
			var errors = $.parseJSON(data.responseText)
			apply_errors_form(errors)
		}
	});
	return false;
}


function guardar_formulario_file(accion, form){
	console.log(form)
	console.log(accion)

	$('#'+form).ajaxSubmit({
		dataType: 'json',
		beforeSubmit: function(){
			console.log('enviando')
		},
		success: function(data){
			if (accion == 'create') {
				clear_form('#'+form)
			}
			clear_errors_form('#'+form)

			notification_toast('success', 'ÉXITO', 'guardado correctamente')
		},
		error: function(data, textStatus, jqXHR) {
			clear_errors_form('#'+form)
			var errors = $.parseJSON(data.responseText)
			apply_errors_form(errors)
		}
	})
}

function format_select(config){
	if(config.select != null){
		$("#"+config.select).select2({
			data: config.data == null ? [] : config.data,
			placeholder: config.placeholder == null ? 'Seleccionar' : config.placeholder,
		});
	} 
}




function asd(){
	console.log('asd')
// if ($('#min').val() != null && $('#max').val() != null && $('#min').val() != '' && $('#max').val() != ''){
	// console.log('asd')
	$.fn.dataTableExt.afnFiltering.push(
		function( oSettings, aData, iDataIndex ) {


			var today = new Date();
			var dd = today.getDate();
			var mm = today.getMonth() + 1;
			var yyyy = today.getFullYear();

			if (dd<10)
				dd = '0'+dd;

			if (mm<10)
				mm = '0'+mm;

			today = mm+'/'+dd+'/'+yyyy;

			if ($('#min').val() != '' && $('#max').val() != '' && $('#min').val() != null && $('#max').val() != null) {	

				console.log('mo caca')
				var iMin_temp = $('#min').val();
				if (iMin_temp == '') {
					iMin_temp = '01/01/1980';
				}

				var iMax_temp = $('#max').val();
				if (iMax_temp == '') {
					iMax_temp = today;
				}

				var arr_min = iMin_temp.split("/");
				var arr_max = iMax_temp.split("/");
				var arr_date = aData[3].split("-");

				var iMin = new Date(arr_min[2], arr_min[0], arr_min[1], 0, 0, 0, 0)
				var iMax = new Date(arr_max[2], arr_max[0], arr_max[1], 0, 0, 0, 0)
				var iDate = new Date(arr_date[0], arr_date[1], arr_date[2], 0, 0, 0, 0)

				if ( iMin == "" && iMax == "" )
				{
					return true;
				}
				else if ( iMin == "" && iDate < iMax )
				{
					return true;
				}
				else if ( iMin <= iDate && "" == iMax )
				{
					return true;
				}
				else if ( iMin <= iDate && iDate <= iMax )
				{
					return true;
				}
				return false;
			}else{
				console.log('caca')
			}
		}
		);
// };
}