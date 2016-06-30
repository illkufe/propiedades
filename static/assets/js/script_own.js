$('td.delete input[type=checkbox]').hide()

$('.format-rut').rut({
	formatOn: 'keyup',
	validateOn: 'blur'
}).on('rutInvalido', function(){
	error_msg = $("<li /> ").addClass("errorlist").text('Rut invalido');
	$(this).closest('.form-group').find('.container-error').text('')
	$(this).closest('.form-group').find('.container-error').append(error_msg)
	$(this).val('')
}).on('rutValido', function(){
	$(this).closest('.form-group').find('.container-error').text('')
});

$('.format-date').datepicker({
	todayBtn: 'linked',
	keyboardNavigation: false,
	forceParse: false,
	calendarWeeks: true,
	autoclose: true,
	format: 'dd/mm/yyyy',
});

$('#date_range .input-daterange').datepicker({
	keyboardNavigation: false,
	forceParse: false,
	autoclose: true,
	format: 'dd/mm/yyyy',
});


$(".file-format").filestyle({
	placeholder: "Seleccionar Archivo",
	buttonText: ""
});


var language = {
	'emptyTable': 'Sin Datos',
	'info': 'mostranto _END_ de _TOTAL_ registros',
	'infoEmpty': '0-0 de 0',
	'infoFiltered': '',
	'infoPostFix': '',
	'thousands': ',',
	'lengthMenu': '_MENU_',
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
		
		// var input = $("#id_" + index),
		// container = $("#div_id_" + index),
		error_msg = value[0]
		$("#id_" + index).closest('.form-group').find('.container-error').append(error_msg)
		
	});
}

function clear_errors_form(form){
	$(form +' '+ '.container-error').html('')
}

function clear_form(form){
	// inputs y selects normales
	$(form +' '+ '.form-group input').val('')
	$(form +' '+ '.form-group textarea').val('')
	$(form +' '+ 'select option:first-child').prop('selected', true);
	// inputs y selects formularios hijos
	$(form +' '+ 'tbody input').val('')
	// select 2
	$('.select2').val(null).trigger("change")
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


function guardar_formulario_final(accion, entidad){

	$.ajax({
		type: 'post',
		url: $('#form-'+entidad+'-new').attr('action'),
		data: $('#form-'+entidad+'-new').serialize(),
		success: function(data) {

			if (accion == 'create') {
				clear_form('#form-'+entidad+'-new')
			}
			else if(accion == 'modal'){
				$('#m-'+entidad+'-new').modal('hide')
				$('#id_'+entidad+'').append($("<option selected></option>").attr("value",data.id).text(data.nombre))
			}
			else{

			}

			clear_errors_form('#form-'+entidad+'-new')
			notification_toast('success', 'ÉXITO', 'guardado correctamente')
		},
		error: function(data, textStatus, jqXHR) {
			clear_errors_form('#form-'+entidad+'-new')
			var errors = $.parseJSON(data.responseText)
			apply_errors_form(errors)
		}
	});
	return false;
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

	$('#'+form).ajaxSubmit({
		dataType: 'json',
		beforeSubmit: function(){
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


function agregar_fila(tabla, entidad){

	var count 	= $('#'+tabla+' tbody').children().length;
	var $tr 	= $('#'+tabla+' tbody tr:first');
	var $clone 	= $tr.clone();
	var row 	= $clone.html().replace(/_set-0/g, '_set-'+count);
	var $row 	= $(row)

	$row.find('input').val('');
	$row.find('select option:first-child').attr("selected", "selected");
	$row.find('input:checkbox').prop('checked',false);

	$('#'+tabla+' tbody').append('<tr></tr>')
	$('#'+tabla+' tbody tr:last').append($row)

	var cantidad = parseInt($('#id_'+entidad+'_set-TOTAL_FORMS').val())
	cantidad += 1
	$('#id_'+entidad+'_set-TOTAL_FORMS').val(cantidad)

}

