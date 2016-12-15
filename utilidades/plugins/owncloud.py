import owncloud
import os

# code description
# 1 = conection owncloud
# 2 = list directory
# 3 = create folder
# 4 = delete folder or file
# 5 = upload file

def oc_conection(data):

	oc = None

	try:
		oc 		= owncloud.Client(data['url'])
		oc.login(data['username'], data['password'])
		status 	= True
		message = 'correcto'

	except Exception as error:

		status 	= False
		message = 'verificar configuración de conexión'

	return {
		'response' : {
			'status' 	: status,
			'message' 	: message,
			'phase' 	: 1
			},
		'data' : oc,
	}

def oc_list_directory(oc_name, oc_path, data_conection):

	data 	= list()
	oc 		= oc_conection(data_conection)
	message = 'correcto'
	status 	= True
	phase 	= 2

	if oc['response']['status']:
		try:
			elements   = oc['data'].list(oc_path)
			children   = oc_files_in_directory(elements, oc['data'])

			data = [{
				'text'	: oc_name,
				'icon'	: 'fa fa-folder',
				'data' 	: {
					'type' 	: 'folder',
					'path' 	: oc_path,
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
		except Exception as error:

			message = 'no existe la carpeta'
			status 	= False
	else:
		message = oc['response']['message']
		status 	= oc['response']['status']
		phase 	= oc['response']['phase']

	return {
		'response' : {
			'status'	: status,
			'message'	: message,
			'phase'		: phase,
		},
		'data': data
	}

def oc_files_in_directory(oc_element, oc):

	response = list()

	for item in oc_element:

		share = oc.share_file_with_link(item.path)

		if item.is_dir():

			elements 	= oc.list(item.path)
			directory 	= oc_files_in_directory(elements, oc)

			response.append({
				'text'	: item.name,
				'icon' 	: 'fa fa-folder',
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
				'icon'	: oc_info_file(item.name)['icon'],
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

def oc_create_directory(oc_path, oc_name, data_conection):

	oc 		= oc_conection(data_conection)
	phase 	= 3

	if oc['response']['status']:

		path = str(oc_path) + '/' + str(oc_name)

		try:

			oc['data'].mkdir(path)
			status  = True
			message = 'correcto'

		except Exception as error:

			status  = False
			message = 'no se pudo crear la carpeta'
			
	else:
		
		status 	= oc['response']['status']
		message = oc['response']['message']
		phase  	= oc['response']['phase']

	return {
		'status'	: status,
		'message'	: message,
		'phase'		: phase,
	}

def oc_delete(oc_path, oc_name, oc_type, data_conection):

	oc 		= oc_conection(data_conection)
	phase 	= 4

	if oc['response']['status']:

		try:

			path 	= str(oc_path) if oc_type == 'folder' else str(oc_path) + '/' + str(oc_name)
			oc['data'].delete(path)
			status  = True
			message = 'correcto'

		except Exception as error:

			status  = False
			message = 'no se pudo eliminar el archivo o carpeta'

	else:

		status 	= oc['response']['status']
		message = oc['response']['message']
		phase  	= oc['response']['phase']

	return {
		'status'	: status,
		'message'	: message,
		'phase'		: phase,
	}

def oc_upload_file(oc_path, source_file, data_conection, **kwargs):

	oc 		= oc_conection(data_conection)
	phase 	= 5

	if oc['response']['status']:

		try:

			oc['data'].put_file(oc_path, source_file, **kwargs)
			status  = True
			message = 'correcto'

		except Exception as error:

			status  = False
			message = 'no se pudo subir el archivo'

	else:

		status 	= oc['response']['status']
		message = oc['response']['message']
		phase  	= oc['response']['phase']

	return {
		'status'	: status,
		'message'	: message,
		'phase'		: phase,
	}

def oc_info_file(name):

	info_file = {
		'file' : {
			'icon' : 'fa fa-file-o',
		},
		'pdf' : {
			'icon' : 'fa fa-file-pdf-o',
		},
		'xls' : {
			'icon' : 'fa fa-file-excel-o',
		},
		'xlsx' : {
			'icon' : 'fa fa-file-excel-o',
		},
		'doc' : {
			'icon' : 'fa fa-file-word-o',
		},
		'txt' : {
			'icon' : 'fa fa-file-text-o',
		},
		'png' : {
			'icon' : 'fa fa-file-image-o',
		}
	}

	name, extension = os.path.splitext(name)
	extension	 	= extension.replace('.', '')

	return info_file.get('file') if info_file.get(extension, False) is False else info_file.get(extension)

def oc_path_exists(oc_path, data_conection):

	try:
		oc = oc_conection(data_conection)
		oc['data'].file_info(oc_path)

		status 	= True
		message = 'correcto'
		
	except Exception as error:

		status 	= False
		message = error

	return {
		'status'	: status,
		'message'	: message,
	}
