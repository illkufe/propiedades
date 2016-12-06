from datetime import datetime
import owncloud

def oc_conection():

	oc = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
	oc.login('enunez', 'asgard2016')
	
	return oc

def oc_list_directory(oc_name, oc_path):

    oc 			= oc_conection()
    elements	= oc.list(oc_path)
    children 	= oc_files_in_directory(elements, oc)

    data = [{
        'text': oc_name,
        'data' : {
            'type' : 'folder',
            'permissions' : {
                'edit' 		: False,
                'remove' 	: False,
            },
        },
        'state': {
            'opened': True
        },
        'children': children,
    }]

    return data

def oc_files_in_directory(oc_element, oc):

    response = list()

    for item in oc_element:

        share = oc.share_file_with_link(item.path)

        if item.is_dir():

            elements 	= oc.list(item.path)
            directory 	= oc_files_in_directory(elements, oc)

            response.append({
				'text'	: item.name,
				'data' 	: {
					'type'	: 'folder',
					'id' 	: share.get_id(),
					'name'	: item.get_name(),
					'path'	: item.get_path(),
					'link'	: share.get_link(),
					'permissions' : {
						'edit' 		: True,
						'remove' 	: True,
						},
					},
				'state': {
					'opened': True
				},
				'children': directory,
				})
        else:

            response.append({
				'text'	: item.name,
				'type' 	: 'html',
				'data' 	: {
					'type'	: 'file',
					'id' 	: share.get_id(),
					'name'	: item.get_name(),
					'path'	: item.get_path(),
					'link'	: share.get_link(),
					'permissions' : {
						'edit' 		: True,
						'remove' 	: True,
						},
					}
				})
    return response

def oc_create_directory(oc_path, oc_name):

	messages = [
		'correcto',
		'error: no se pudo crear la carpeta',
	]

	path 	= str(oc_path) + '/' + str(oc_name)
	oc 		= oc_conection()

	try:

		if oc.mkdir(path):
			status  = True
			message = 0

		else:
			status  = False
			message = 1
	except Exception:

		status  = False
		message = 1

	return {
		'status' 	: status,
		'message' 	: messages[message],
	}

def oc_delete(oc_path, oc_name, oc_type):

	messages = [
		'correcto',
		'error: no se pudo eliminar el archivo y/o carpeta',
	]

	path 	= str(oc_path) if oc_type == 'folder' else str(oc_path) + '/' + str(oc_name)
	oc 		= oc_conection()

	try:

		if oc.delete(path):
			status  = True
			message = 0

		else:
			status  = False
			message = 1

	except Exception:
		status  = False
		message = 1

	return {
		'status' 	: status,
		'message' 	: messages[message],
	}

def oc_upload_file(oc_path, source_file, **kwargs):

	messages = [
		'correcto',
		'error: no se pudo crear la carpeta',
	]

	oc = oc_conection()

	try:		
		if oc.put_file(oc_path, source_file, **kwargs):
			status  = False
			message = 1

		else:
			status  = False
			message = 1

	except Exception:
		status  = False
		message = 1
		

	return {
		'status' 	: status,
		'message' 	: messages[message],
	}



# def create_directory(path_owncloud_directory, name_directory):

# 	"""
# 		función que permite realiza la creación de un directorio owncloud.
# 	:param path_owncloud_directory: ruta del directorio base
# 	:param name_directory: nombre de la carpeta a crear
# 	:return: objeto con un estado del proceso y una descripcion del error.
# 	"""

# 	data    = list()
# 	error   = None
# 	oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 	oc.login('enunez', 'asgard2016')

# 	# try:

# 	if not path_owncloud_directory.endswith('/'):
# 		path_owncloud_directory += '/'

# 	path_owncloud_directory = path_owncloud_directory + str(name_directory)
# 		# file_info               = oc.file_info(path_owncloud_directory)

# 		#Existe directorio
# 		# if not file_info:
# 	try:
# 		status = oc.mkdir(path_owncloud_directory)
# 		if status:
# 			data.append({
# 				'estado': True,
# 				'error' : error
# 			})
# 		else:
# 			error = 'Error en la creación del directorio'
# 			data.append({
# 				'estado': False,
# 				'error' : error
# 			})
# 	except Exception:
# 		error = 'Error en la creación del directorio'
# 		data.append({
# 			'estado': False,
# 			'error': error
# 		})
# 		# else:
# 		# 	error = 'Directorio ya existe.'
# 		# 	data.append({
# 		# 		'estado': False,
# 		# 		'error': error
# 		# 	})

# 	# except Exception:

# 	# 	error = 'Directorio ya existe.'
# 	# 	data.append({
# 	# 		'estado': False,
# 	# 		'error': error
# 	# 	})

# 	return data

# def delete_directory(path_owncloud_directory, name_directory):
# 	"""
# 		función que permite realizar la eliminacion de un directorio o archivo
# 	:param path_owncloud_directory: ruta base del directorio
# 	:param name_directory: nombre de la carpeta o archivo a eliminar
# 	:return: objeto con un estado del proceso y una descripcion del error.
# 	"""

# 	data    = list()
# 	error   = None
# 	oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 	oc.login('enunez', 'asgard2016')

# 	try:
# 		path_owncloud_directory = path_owncloud_directory + str(name_directory)
# 		file_info               = oc.file_info(path_owncloud_directory)

# 		if file_info:
# 			try:
# 				status = oc.delete(path_owncloud_directory)

# 				if status:
# 					data.append({
# 						'estado': True,
# 						'error' : error
# 					})
# 				else:
# 					error = 'Error en la eliminación del directorio'
# 					data.append({
# 						'estado': False,
# 						'error' : error
# 					})
# 			except Exception:
# 				error = 'Error en la eliminación del directorio'
# 				data.append({
# 					'estado': False,
# 					'error': error
# 				})
# 		else:
# 			error = 'Archivo o directorio no se encuentra.'
# 			data.append({
# 				'estado': False,
# 				'error' : error
# 			})

# 	except Exception:
# 		error = 'Directorio No existe.'
# 		data.append({
# 			'estado' : False,
# 			'error'  : error
# 		})

# 	return data

# def backups_directory(path_owncloud_directory, name_directory, path_directory_backups):
# 	"""
# 		función que permite realizar el backup de una carpeta en un directorio de respaldos.
# 	:param path: ruta del directorio base
# 	:param name_directory: nombre de la carpeta a crear
# 	:param path_directory_backups: ruta del directorio de respaldo
# 	:return: objeto con un estado del proceso y una descripcion del error.
# 	"""
# 	try:
# 		data    = list()
# 		error   = None
# 		oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 		oc.login('enunez', 'asgard2016')

# 		path_owncloud_directory                = path_owncloud_directory + str(name_directory)

# 		if not path_directory_backups.endswith('/'):
# 			path_directory_backups += '/'

# 		if not path_owncloud_directory.endswith('/'):
# 			path_owncloud_directory += '/'


# 		try:
# 			directory_info          = oc.file_info(path_directory_backups)

# 			#Directorio de respaldo Existe
# 			if directory_info:
# 				try:
# 					# Creacion de carpeta backup del activo en respaldo
# 					path_directory_backups  = path_directory_backups + name_directory + '_' + datetime.now().strftime('%d-%m-%Y %I:%M:%S') + '/'
# 					status_dir              = oc.mkdir(path_directory_backups)
# 					if status_dir:
# 						try:
# 							# Copia de archivos y posterior eliminacion de la carpeta original del directorio
# 							status_copy             = oc.copy(path_owncloud_directory, path_directory_backups)
# 							status_delete           = oc.delete(path_owncloud_directory[:-1])
# 							if status_copy and status_delete:
# 								data.append({
# 									'estado': True,
# 									'error' : error
# 								})
# 							else:
# 								error = 'Error en creación de respaldo de activo'
# 								data.append({
# 									'estado': False,
# 									'error': error
# 								})
# 						except Exception:
# 							error = 'Error en creación de respaldo de activo'
# 							data.append({
# 								'estado': False,
# 								'error': error
# 							})
# 					else:
# 						error = 'Error en creación de directorio del activo en carpeta de respaldos'
# 						data.append({
# 							'estado': False,
# 							'error': error
# 						})
# 				except Exception:
# 					error = 'Error en creación de directorio del activo en carpeta de respaldos'
# 					data.append({
# 						'estado': False,
# 						'error': error
# 					})
# 		except Exception:

# 			try:
# 				# Creacion de directorio de respaldos
# 				status_dir = oc.mkdir(path_directory_backups)
# 				if status_dir:
# 					try:
# 						#Creacion de carpeta backup del activo en respaldo
# 						path_directory_backups  = path_directory_backups + name_directory + '_' + datetime.now().strftime('%d-%m-%Y') + '/'
# 						status_dir              = oc.mkdir(path_directory_backups)
# 						if status_dir:

# 							try:
# 								#Copia de archivos y posterior eliminacion de la carpeta original del directorio
# 								status_copy     = oc.copy(path_owncloud_directory, path_directory_backups)
# 								status_delete   = oc.delete(path_owncloud_directory[:-1])

# 								if status_copy and status_delete:
# 									data.append({
# 										'estado': True,
# 										'error': error
# 									})
# 								else:
# 									error = 'Error realizacion del respaldo del activo'
# 									data.append({
# 										'estado': False,
# 										'error': error
# 									})
# 							except Exception:
# 								error = 'Error realizacion del respaldo del activo'
# 								data.append({
# 									'estado': False,
# 									'error': error
# 								})
# 						else:
# 							error = 'Error en creación de directorio del activo en carpeta de respaldos.'
# 							data.append({
# 								'estado': False,
# 								'error': error
# 							})
# 					except Exception:
# 						error = 'Error en creación de directorio del activo en carpeta de respaldos.'
# 						data.append({
# 							'estado': False,
# 							'error': error
# 						})
# 				else:
# 					error = 'Error en la creación del directorio respaldo.'
# 					data.append({
# 						'estado': False,
# 						'error': error
# 					})
# 			except Exception:
# 				error = 'Error en la creación del directorio respaldo'
# 				data.append({
# 					'estado': False,
# 					'error': error
# 				})

# 	except Exception as e:
# 		error = 'Error respaldo del activo'
# 		data.append({
# 			'estado' : False,
# 			'error'  : error
# 		})

# 	return data

# def upload_directory(path_owncloud_directory, path_local_directory, **kwargs):

# 	data    = list()
# 	error   = None
# 	oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 	oc.login('enunez', 'asgard2016')

# 	try:

# 		directory_info = oc.file_info(path_owncloud_directory)

# 		if directory_info:
# 			try:
# 				status_upload   = oc.put_directory(path_owncloud_directory, path_local_directory, **kwargs)
# 				if status_upload:
# 					data.append({
# 						'estado': True,
# 						'error': error
# 					})
# 				else:
# 					error = 'No se pudo subir directorio a Owncloud'
# 					data.append({
# 						'estado': False,
# 						'error': error
# 					})
# 			except Exception:
# 				error = 'No se pudo subir directorio a Owncloud'
# 				data.append({
# 					'estado': False,
# 					'error': error
# 				})
# 		else:
# 			error = 'Directorio Owncloud no existe.'
# 			data.append({
# 				'estado': False,
# 				'error': error
# 			})
# 	except Exception:
# 		error = 'Directorio Owncloud no existe.'
# 		data.append({
# 			'estado': False,
# 			'error': error
# 		})

# 	return data

# def upload_file(path_owncloud_directory, local_source_file,**kwargs):

# 	data    = list()
# 	error   = None
# 	oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 	oc.login('enunez', 'asgard2016')

# 	try:

# 		directory_info = oc.file_info(path_owncloud_directory)

# 		if directory_info:
# 			try:
# 				status_upload   = oc.put_file(path_owncloud_directory, local_source_file, **kwargs)
# 				if status_upload:
# 					data.append({
# 						'estado': True,
# 						'error': error
# 					})
# 				else:
# 					error = 'No se pudo subir el archivo a Owncloud'
# 					data.append({
# 						'estado': False,
# 						'error': error
# 					})
# 			except Exception:
# 				error = 'No se pudo subir el archivo a Owncloud'
# 				data.append({
# 					'estado': False,
# 					'error': error
# 				})
# 		else:
# 			error = 'Directorio Owncloud no existe.'
# 			data.append({
# 				'estado': False,
# 				'error': error
# 			})
# 	except Exception:
# 		error = 'Directorio Owncloud no existe.'
# 		data.append({
# 			'estado': False,
# 			'error': error
# 		})

# 	return data

# def download_directory_as_zip(path_owncloud_directory, path_local):

# 	data    = list()
# 	error   = None
# 	oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 	oc.login('enunez', 'asgard2016')

# 	try:

# 		directory_info = oc.file_info(path_owncloud_directory)

# 		if directory_info:
# 			try:
# 				status_download   = oc.get_directory_as_zip(path_owncloud_directory, path_local)
# 				if status_download:
# 					data.append({
# 						'estado': True,
# 						'error': error
# 					})
# 				else:
# 					error = 'No se pudo descargar la carpeta desde Owncloud'
# 					data.append({
# 						'estado': False,
# 						'error': error
# 					})
# 			except Exception:
# 				error = 'No se pudo descargar la carpeta desde Owncloud'
# 				data.append({
# 					'estado': False,
# 					'error': error
# 				})
# 		else:
# 			error = 'Directorio Owncloud no existe.'
# 			data.append({
# 				'estado': False,
# 				'error': error
# 			})
# 	except Exception:
# 		error = 'Directorio Owncloud no existe.'
# 		data.append({
# 			'estado': False,
# 			'error': error
# 		})

# 	return data

# def download_file(path_owncloud_directory, path_local=None):

# 	data    = list()
# 	error   = None
# 	oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
# 	oc.login('enunez', 'asgard2016')

# 	try:

# 		directory_info = oc.file_info(path_owncloud_directory)

# 		if directory_info:
# 			try:
# 				status_download   = oc.get_file(path_owncloud_directory, path_local)
# 				if status_download:
# 					data.append({
# 						'estado': True,
# 						'error': error
# 					})
# 				else:
# 					error = 'No se pudo descargar el archivo desde Owncloud'
# 					data.append({
# 						'estado': False,
# 						'error': error
# 					})
# 			except Exception:
# 				error = 'No se pudo descargar el archivo desde Owncloud'
# 				data.append({
# 					'estado': False,
# 					'error': error
# 				})
# 		else:
# 			error = 'Directorio Owncloud no existe.'
# 			data.append({
# 				'estado': False,
# 				'error': error
# 			})
# 	except Exception:
# 		error = 'Directorio Owncloud no existe.'
# 		data.append({
# 			'estado': False,
# 			'error': error
# 		})

# 	return data
