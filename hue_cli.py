#!/usr/bin/python
import sys
from hue_cli import auth
from hue_cli import filebrowser
import sys





if __name__=="__main__":	
	verb = sys.argv[1]

	verbs = {
		"login": auth.login,
		"listdir": filebrowser.listdir,
		"download": filebrowser.download,
		"upload": filebrowser.upload,
		"touch": filebrowser.touch,
		"mkdir": filebrowser.mkdir
	}
	
	if verb not in verbs:
		print("availables commands:")
		print("\t" + ("\n\t").join(verbs.keys()))
		sys.exit(1)

	fn = verbs[verb]
	fn(sys.argv[2:])	