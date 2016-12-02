from datetime import datetime
import owncloud


def create_directory(path, name_directory):

    """
        función que permite realiza la creación de un directorio owncloud.
    :param path: ruta del directorio base
    :param name_directory: nombre de la carpeta a crear
    :return: objeto con un estado del proceso y una descripcion del error.
    """

    data    = list()
    error   = None
    oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
    oc.login('enunez', 'asgard2016')

    try:

        if not path.endswith('/'):
            path += '/'

        path        = path + str(name_directory)
        file_info   = oc.file_info(path)

        #Existe directorio
        if not file_info:
            try:
                status = oc.mkdir(path)
                if status:
                    data.append({
                        'estado': True,
                        'error' : error
                    })
                else:
                    error = 'Error en la creación del directorio'
                    data.append({
                        'estado': False,
                        'error' : error
                    })
            except Exception:
                error = 'Error en la creación del directorio'
                data.append({
                    'estado': False,
                    'error': error
                })
        else:
            error = 'Directorio ya existe.'
            data.append({
                'estado': False,
                'error': error
            })

    except Exception:

        error = 'Directorio ya existe.'
        data.append({
            'estado': False,
            'error': error
        })

    return data

def delete_directory(path, name_directory):
    """
        función que permite realizar la eliminacion de un directorio o archivo
    :param path: ruta base del directorio
    :param name_directory: nombre de la carpeta o archivo a eliminar
    :return: objeto con un estado del proceso y una descripcion del error.
    """

    data    = list()
    error   = None
    oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
    oc.login('enunez', 'asgard2016')

    try:
        path        = path + str(name_directory)
        file_info   = oc.file_info(path)

        if file_info:
            try:
                status = oc.delete(path)

                if status:
                    data.append({
                        'estado': True,
                        'error' : error
                    })
                else:
                    error = 'Error en la eliminación del directorio'
                    data.append({
                        'estado': False,
                        'error' : error
                    })
            except Exception:
                error = 'Error en la eliminación del directorio'
                data.append({
                    'estado': False,
                    'error': error
                })
        else:
            error = 'Archivo o directorio no se encuentra.'
            data.append({
                'estado': False,
                'error' : error
            })

    except Exception:
        error = 'Directorio No existe.'
        data.append({
            'estado' : False,
            'error'  : error
        })

    return data

def backups_directory(path, name_directory, path_directory_backups):
    """
        función que permite realizar el backup de una carpeta en un directorio de respaldos.
    :param path: ruta del directorio base
    :param name_directory: nombre de la carpeta a crear
    :param path_directory_backups: ruta del directorio de respaldo
    :return: objeto con un estado del proceso y una descripcion del error.
    """
    try:
        data    = list()
        error   = None
        oc      = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
        oc.login('enunez', 'asgard2016')

        path                = path + str(name_directory)

        if not path_directory_backups.endswith('/'):
            path_directory_backups += '/'

        if not path.endswith('/'):
            path += '/'


        try:
            directory_info          = oc.file_info(path_directory_backups)

            #Directorio de respaldo Existe
            if directory_info:
                try:
                    # Creacion de carpeta backup del activo en respaldo
                    path_directory_backups  = path_directory_backups + name_directory + '_' + datetime.now().strftime('%d-%m-%Y %I:%M:%S') + '/'
                    status_dir              = oc.mkdir(path_directory_backups)
                    if status_dir:
                        try:
                            # Copia de archivos y posterior eliminacion de la carpeta original del directorio
                            status_copy             = oc.copy(path, path_directory_backups)
                            status_delete           = oc.delete(path[:-1])
                            if status_copy and status_delete:
                                data.append({
                                    'estado': True,
                                    'error' : error
                                })
                            else:
                                error = 'Error en creación de respaldo de activo'
                                data.append({
                                    'estado': False,
                                    'error': error
                                })
                        except Exception:
                            error = 'Error en creación de respaldo de activo'
                            data.append({
                                'estado': False,
                                'error': error
                            })
                    else:
                        error = 'Error en creación de directorio del activo en carpeta de respaldos'
                        data.append({
                            'estado': False,
                            'error': error
                        })
                except Exception:
                    error = 'Error en creación de directorio del activo en carpeta de respaldos'
                    data.append({
                        'estado': False,
                        'error': error
                    })
        except Exception:

            try:
                # Creacion de directorio de respaldos
                status_dir = oc.mkdir(path_directory_backups)
                if status_dir:
                    try:
                        #Creacion de carpeta backup del activo en respaldo
                        path_directory_backups  = path_directory_backups + name_directory + '_' + datetime.now().strftime('%d-%m-%Y') + '/'
                        status_dir              = oc.mkdir(path_directory_backups)
                        if status_dir:

                            try:
                                #Copia de archivos y posterior eliminacion de la carpeta original del directorio
                                status_copy     = oc.copy(path, path_directory_backups)
                                status_delete   = oc.delete(path[:-1])

                                if status_copy and status_delete:
                                    data.append({
                                        'estado': True,
                                        'error': error
                                    })
                                else:
                                    error = 'Error realizacion del respaldo del activo'
                                    data.append({
                                        'estado': False,
                                        'error': error
                                    })
                            except Exception:
                                error = 'Error realizacion del respaldo del activo'
                                data.append({
                                    'estado': False,
                                    'error': error
                                })
                        else:
                            error = 'Error en creación de directorio del activo en carpeta de respaldos.'
                            data.append({
                                'estado': False,
                                'error': error
                            })
                    except Exception:
                        error = 'Error en creación de directorio del activo en carpeta de respaldos.'
                        data.append({
                            'estado': False,
                            'error': error
                        })
                else:
                    error = 'Error en la creación del directorio respaldo.'
                    data.append({
                        'estado': False,
                        'error': error
                    })
            except Exception:
                error = 'Error en la creación del directorio respaldo'
                data.append({
                    'estado': False,
                    'error': error
                })

    except Exception as e:
        error = 'Error respaldo del activo'
        data.append({
            'estado' : False,
            'error'  : error
        })

    return data