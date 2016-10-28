$("span.pie").peity("pie", {
	fill: ['#1ab394', '#d7d7d7', '#ffffff']
})

$('td.delete input[type=checkbox]').hide()

$('.format-number').autoNumeric("init",{
	aSep: LEASE_CURRENCY_THOUSANDS,
	aDec: LEASE_CURRENCY_DECIMALS,
	mDec: LEASE_CURRENCY_FORMAT,
})


function change_config_money(moneda_activa, moneda) {

	if(moneda_activa){
		$.ajax({
			url: '/get/configuracion-monedas/'+moneda,
			type: 'POST',
			data: {csrfmiddlewaretoken: getCookie('csrftoken')},
			success: function(data){
				$('.format-number').autoNumeric("update",{
					aSep: data[0].format_mil,
					aDec: data[0].format_dec,
					mDec: data[0].decimal,
            	})
			},
			error:function(data){
				var configuracion = {
					'toast_type'	: 'error',
					'toast_text' 	: 'no se puedo recuperar configuración de monedas',
					'toast_title' 	: 'Error',
				}
				notification_toast(configuracion)
			}
		})
	}else{
		$('.format-number').autoNumeric("init",{
			aSep: LEASE_CURRENCY_THOUSANDS,
			aDec: LEASE_CURRENCY_DECIMALS,
			mDec: LEASE_CURRENCY_FORMAT,
		})
	}
}


function cambio_format_moneda(obj) {

    var moneda = parseInt($(obj).val())

    if(! isNaN(moneda)){
       change_config_money_selected(moneda, obj)
    }
}

function change_config_money_selected(moneda, obj) {

	$('.format-number').autoNumeric("init",{
		aSep: LEASE_CURRENCY_THOUSANDS,
		aDec: LEASE_CURRENCY_DECIMALS,
		mDec: LEASE_CURRENCY_FORMAT,
	})

    $.ajax({
        url: '/get/configuracion-monedas/'+moneda,
        type: 'POST',
        data: {csrfmiddlewaretoken: getCookie('csrftoken')},
        success: function(data){
            $(obj).closest('tr').find('.format-number').autoNumeric("update",{
                aSep: data[0].format_mil,
                aDec: data[0].format_dec,
                mDec: data[0].decimal,
            })
        },
        error:function(data){
            var configuracion = {
                'toast_type'	: 'error',
                'toast_text' 	: 'no se puedo recuperar configuración de monedas',
                'toast_title' 	: 'Error',
            }
            notification_toast(configuracion)
        }
    })
}

$('.format-rut').rut({
	formatOn: 'keyup',
	validateOn: 'blur'
}).on('rutInvalido', function(){
	$(this).closest('.form-group').find('.container-error').text('')
	$(this).closest('.form-group').find('.container-error').append('rut invalido')
	$(this).val('')
}).on('rutValido', function(){
	$(this).closest('.form-group').find('.container-error').text('')
});

$('.format-date').datepicker({
	language: "es",
	todayBtn: 'linked',
	keyboardNavigation: false,
	forceParse: false,
	calendarWeeks: true,
	autoclose: true,
	format: 'dd/mm/yyyy',
});

$('#date_range .input-daterange').datepicker({
	language: "es",
	keyboardNavigation: false,
	forceParse: false,
	autoclose: true,
	format: 'dd/mm/yyyy',
});

$('.format-datetime').datetimepicker({
	format: 'DD/MM/YYYY HH:mm',
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



$('.format-ip').mask('0ZZ.0ZZ.0ZZ.0ZZ', {
    translation: {
      'Z': {
        pattern: /[0-9]/, optional: true
      }
    }
});



function apply_errors_form(errors){
	
	$.each(errors, function(index, value) {
		console.log(index)
		
		// var input = $("#id_" + index),
		// container = $("#div_id_" + index),
		error_msg = value[0]
		// console.log(error_msg)
		$("#id_" + index).closest('.form-group').find('.container-error').append(error_msg)
		
	});
}

function clear_errors_form(form){

	$(form +' '+ '.container-error').html('')
}

function clear_form(form){
	// inputs y selects normales
	$(form +' '+ '.form-group input[type="number"]').val('')
	$(form +' '+ '.form-group input[type="text"]').val('')
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
		'ordering': configuracion.ordering == null  ? true : configuracion.ordering,
		'order': configuracion.order == null ? [[0, 'desc']] : configuracion.order,
		'paginate': configuracion.paginate == null  ? true : configuracion.paginate,
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
		confirmButtonColor: '#F8BB86',
		cancelButtonColor: '#D0D0D0',
		confirmButtonText: 'Si, eliminar',
		cancelButtonText: 'Cancelar',
		closeOnConfirm: true,
	}).then(function() {
		$.ajax({
			url: '/'+model+'/delete/'+id,
			type: 'POST',
			data: {csrfmiddlewaretoken: getCookie('csrftoken')},
			success: function(data){
				var table = $('#'+tabla).DataTable();
				table.row($(col)).remove().draw();

				var configuracion = {
					'toast_type'	: 'success',
					'toast_text' 	: 'eliminado correctamente',
					'toast_title' 	: 'Éxito',
				}
				notification_toast(configuracion)
			},
			error:function(data){
				var configuracion = {
					'toast_type'	: 'error',
					'toast_text' 	: 'no se puedo eliminar',
					'toast_title' 	: 'Error',
				}
				notification_toast(configuracion)
			}
		})
	})
}

function open_modal_delete_child(obj, text){

	swal({
		title: '¿ Eliminar '+text+' ?',
		text: '',
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#F8BB86',
		cancelButtonColor: '#D0D0D0',
		confirmButtonText: 'Si, eliminar',
		cancelButtonText: 'Cancelar',
		closeOnConfirm: true,
	}).then(function() {
		$(obj).closest('tr').find('input:checkbox:last').prop('checked', true)
		$(obj).closest('tr').addClass('hide')
	});	
}

function open_modal_delete_child_final(obj, text, tipo){

	swal({
		title: '¿ Eliminar '+text+' ?',
		text: '',
		type: 'warning',
		showCancelButton: true,
		confirmButtonColor: '#F8BB86',
		cancelButtonColor: '#D0D0D0',
		confirmButtonText: 'Si, eliminar',
		cancelButtonText: 'Cancelar',
		closeOnConfirm: true,
	}).then(function() {
		if(tipo == 'new'){
			$(obj).closest('tr').remove()

		}else{
			$(obj).closest('tr').find('input:checkbox:last').prop('checked', true)
			$(obj).closest('tr').addClass('hide')
		}
	});	
}

function guardar_formulario_final(accion, entidad){

	$.ajax({
		type: 'post',
		url: $('#form-'+entidad+'-new').attr('action'),
		data: $('#form-'+entidad+'-new').serialize(),
		success: function(data) {
			console.log(data)

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
			var configuracion = {
				'toast_type'	: 'success',
				'toast_text' 	: 'guardado correctamente',
				'toast_title' 	: 'Éxito',
			}
			notification_toast(configuracion)
		},
		error: function(data, textStatus, jqXHR) {
			console.log('error')
			clear_errors_form('#form-'+entidad+'-new')
			var errors = $.parseJSON(data.responseText)
			apply_errors_form(errors)
		}
	});
	return false;
}

function guardar_formulario(accion, form){

	console.log($('#'+form).attr('action'))
	$.ajax({
		type: 'post',
		url: $('#'+form).attr('action'),
		data: $('#'+form).serialize(),
		success: function(response) {
			console.log('ok')
			if (accion == 'create') {
				clear_form('#'+form)
			}
			clear_errors_form('#'+form)
			var configuracion = {
				'toast_type'	: 'success',
				'toast_text' 	: 'guardado correctamente',
				'toast_title' 	: 'Éxito',
			}
			notification_toast(configuracion)
			
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
			
			var configuracion = {
				'toast_type'	: 'success',
				'toast_text' 	: 'guardado correctamente',
				'toast_title' 	: 'Éxito',
			}
			notification_toast(configuracion)
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

function agregar_fila_final(tabla, entidad){

	var count 	= $('#'+tabla+' tbody').children().length;
	var $tr 	= $('#'+tabla+' tbody tr:first');
	var $clone 	= $tr.clone();
	var row 	= $clone.html().replace(/_set-0/g, '_set-'+count).replace(/update/g, 'new');

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

// funciones factorizadas
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

function loading(mostrar) {
	if (mostrar) {
		$.blockUI({
			message: '<h1><i class="fa fa-cog fa-spin fa-1x fa-fw"></i> Por favor espere...</h1>', 
			css: {
				backgroundColor: 'none',
				color: '#fff',
				border:'none',
			}
		});
	}else{
		$.unblockUI();
	}
}

function notification_toast(configuracion){

	toastr.options = {
		"closeButton": true,
		"debug": false,
		"progressBar": true,
		"preventDuplicates": false,
		"positionClass": configuracion.positionClass == null ? "toast-top-right" : configuracion.positionClass,
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

	toastr[configuracion.toast_type](configuracion.toast_text, configuracion.toast_title)
}

function diferencia_entre_meses(fecha_inicio, fecha_termino) {

	var months;

	months = (fecha_termino.getFullYear() - fecha_inicio.getFullYear()) * 12;
	months -= fecha_inicio.getMonth() + 1;
	months += fecha_termino.getMonth() + 1;

	return months <= 0 ? 0 : months;
}

$('[data-toggle="tooltip"]').tooltip();