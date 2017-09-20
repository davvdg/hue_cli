import auth

import requests
import os
cookies = auth.get_session()
hueUrl = 'https://'+ cookies.list_domains()[0]
moduleUrl = hueUrl + '/filebrowser'

def listdir(args):	
	path = ""
	options = []
	if len(args) == 1:
		path = args[0]
	else:
		options = args[:-1]
		path = args[-1]

	flags = {"h": False,
			 "l": False,
			 "s": False}
	for option in options:
		if option.startswith("-"):
			for i in option[1:]:
				flags[i] = True
			#its a flag

	url = moduleUrl + "/listdir=" + path +"?format=json"	
	
	r = requests.get(url, cookies=cookies)
	res = r.json()
	#print res
	files =[]
	directories = []

	for file in res["files"]:

		name = file["name"]
		if name != "":
			if file["type"] == "file":
				files.append(name)
			if file["type"] == "dir":
				directories.append(name)
		if not flags["s"]:
			if name == "":
				name = ".."
			size = str(file["stats"]["size"])
			toPrint = [name]
			if flags["h"]:
				size = file["humansize"].encode('ascii','ignore')
			if flags["l"]:
				toPrint = [file["rwx"], "1", file["stats"]["user"], file["stats"]["group"], size, name]

			print ("\t").join(toPrint)
	return files, directories

def download(args):	
	flags = {"v": False,
			 "r": False}
	fileArgs=[]
	for arg in args:
		if arg.startswith("-"):
			arg = arg[1:]
			if arg.startswith("-"):
				## long flag
				pass
			else:
				for f in arg:
					flags[f] = True
		else:
			fileArgs.append(arg)

	destination = "."
	source = fileArgs[0]
	if len(fileArgs) == 2:
		destination = fileArgs[1]

	if os.path.isdir(destination):
		local_filename = source.split('/')[-1]
		destination += "/" + local_filename
	
	if flags["r"]:
		os.makedirs(destination)
		files, directories = listdir(["-s", source])
		for file in files:
			print destination
			download(["-v", source + "/" + file, destination + "/" + file])
		for directory in directories:
			download(["-rv", source + "/" + directory, destination + "/" + directory])
	else:		
		url = moduleUrl + "/download=" + source
		# NOTE the stream=True parameter
		if flags["v"]:
			print "'%s' -> '%s'" % (source, destination)
		r = requests.get(url, stream=True, cookies=cookies)
		with open(destination, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024): 
				if chunk: # filter out keep-alive new chunks
					f.write(chunk)
					#f.flush() commented by recommendation from J.F.Sebastian
	return destination

def status():
	pass

def stat():
	pass

def upload(args, session=None):
	if session == None:
		session = createPostSession()

	destinationFolder = args[0]
	localFilePaths = args[1]

	if os.path.isdir(localFilePaths):
		print("will create a directory and upload all the files in it.")
		subfiles = os.listdir(localFilePaths)
		mkdir([destinationFolder, localFilePaths], session=session)
		for subfile in subfiles:
			upload([destinationFolder + "/" + localFilePaths, localFilePaths+ "/"+ subfile], session=session)
		return
		#if -r, will recursively upload stuff


	localFilename = os.path.basename(localFilePaths)
	if os.stat(localFilePaths).st_size == 0:
		return touch([destinationFolder, localFilename])
	fh = open(localFilePaths, 'rb')
	files = {'hdfs_file': (localFilename, fh)}
	url = moduleUrl + "/upload/file?dest=" + destinationFolder
	print url
	data = {"dest": destinationFolder}
	r = session.post(url, files=files, data=data, cookies=cookies)
	if r.status_code == 403:
		raise Exception("not autorized")
	if r.status_code == 200:
		result = r.json()
		if result["status"] == -1:
			raise Exception(result["data"])
def createPostSession():
	s = requests.Session()
	s.headers.update({'X-CSRFToken': cookies["csrftoken"]})
	return s

def mkdir(args, session=None):
	if session == None:
		session = createPostSession()

	flags = {"p": False}
	fileArgs=[]
	for arg in args:
		if arg.startswith("-"):
			arg = arg[1:]
			if arg.startswith("-"):
				## long flag
				pass
			else:
				for f in arg:
					flags[f] = True
		else:
			fileArgs.append(arg)
	
	dest = fileArgs[0]
	name = fileArgs[1]
	remains = []

	if flags["p"]:
		sPath = fileArgs[1].split("/")		
		name = sPath.pop(0)
		remains = sPath

	data = {"path": dest, "name": name}
	url = moduleUrl + "/mkdir"	

	r = session.post(url, data=data, cookies=cookies)
	if r.status_code !=200:
		raise Exception("Error creating this folder (possibly already existing)")
	if flags["p"] and len(remains) >0:
		mkdir(["-p", dest + "/" + name, "/".join(remains)], session=session)


def rename():
	pass

def touch(args):
	dest = args[0]
	name = args[1]
	data = {"path": dest, "name": name}
	url = moduleUrl + "/touch"	
	s = requests.Session()
	s.headers.update({'X-CSRFToken': cookies["csrftoken"]})
	r = s.post(url, data=data, cookies=cookies)
	if r.status_code !=200:
		raise Exception("Error Touching this file (possibly already existing)")
	

def move():
	pass

def copy():
	pass

def set_replications():
	pass

def rmtree():
	pass

def chmod():
	pass

def chown():
	pass

