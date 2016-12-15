import owncloud
import os

def oc_conection():

	oc = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
	oc.login('enunez', 'asgard2016')
	
	return oc

def oc_list_directory(oc_name, oc_path):

	status 	= True
	message = 'correcto'
	data 	= list()

	try:

		oc 			= oc_conection()
		elements	= oc.list(oc_path)
		children 	= oc_files_in_directory(elements, oc)

		data.append({
			'text'	: oc_name,
			'icon' 	: 'fa fa-folder',
			'data' 	: {
				'type' 	: 'folder',
				'path'	: oc_path,
				'permissions' : {
					'edit' 		: False,
					'remove' 	: False,
				},
			},
			'state': {
				'opened': True
			},
			'children': children,
		})
	except Exception as e:

		status 	= False
		message = str(e)


	return {
		'status' 	: status,
		'message' 	: message,
		'data'		: data,
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