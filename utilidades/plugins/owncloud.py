import owncloud

def conection(request):

	oc = owncloud.Client('http://ec2-54-211-31-88.compute-1.amazonaws.com/owncloud/')
	oc.login('enunez', 'asgard2016')
	
	return oc

def delete(request, path):

	oc = conection_owncloud(request)
	oc.delete(path)

	return True