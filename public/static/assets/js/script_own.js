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
		'searching': true,
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