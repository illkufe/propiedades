var config = {
		apiKey: "AIzaSyAj7z483ospf7R-8vGshCjCWcanGJLkwDI",
		authDomain: "lease-61711.firebaseapp.com",
		databaseURL: "https://lease-61711.firebaseio.com",
		storageBucket: "lease-61711.appspot.com",
	};

firebase.initializeApp(config);

firebase.auth().signInWithEmailAndPassword('juan.mieres.s@gmail.com', 'juan12345').catch(function(error) {
	var errorCode = error.code;
	var errorMessage = error.message;
});

var alertas = firebase.database().ref('alertas/'+LEASE_USER_ID);

alertas.on('child_added', function(data) {
	agregar_alerta(data)
});

alertas.on('child_removed', function(data) {
	eliminar_alerta(data)
});


function agregar_alerta(data){

	// template
	template = ''
	template += '<li class=@id>'
	template += '<a onclick="mostrar_alerta(\'@id\',\'@mensaje\', \'@emisor\')">'
	template += '<div>'
	template += '<i class="fa fa-envelope fa-fw"></i> @mensaje'
	template += '<span class="pull-right text-muted small">@emisor</span>'
	template += '</div>'
	template += '</a>'
	template += '</li>'
	template += '<li class="@id divider"></li>'
	template += '</span>'

	template = template.replace(/@id/g, data.key);
	template = template.replace(/@mensaje/g, data.val().mensaje);
	template = template.replace(/@emisor/g, data.val().emisor);
	
	// contador
	count = parseInt($('nav.navbar .c-alertas .count-info span').text()) + 1

	$('nav.navbar .c-alertas .count-info span').text(count)
	$('nav.navbar .c-alertas .dropdown-alerts').prepend(template)

}

function eliminar_alerta(data){
	
	// contador
	count = parseInt($('nav.navbar .c-alertas .count-info span').text()) - 1

	$('nav.navbar .c-alertas .count-info span').text(count)
	$('nav.navbar .c-alertas .dropdown-alerts .'+data.key).remove()

}

function mostrar_alerta(id, mensaje, emisor){
	
	var fredRef = firebase.database().ref('alertas/'+LEASE_USER_ID+'/'+id);
	fredRef.remove();

	swal({
		title: mensaje,
		text: emisor,
		type: 'info',
	});
}





