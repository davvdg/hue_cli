import requests
import os, sys
import pickle
home = os.environ["HOME"]
def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
 
def login(args):
	hueURL, login, password = args[0], args[1], args[2]
	next_url = "/"
	login_url = hueURL + "/accounts/login?next=/"

	session = requests.Session()
	r = session.get(login_url)
	form_data = dict(username=login,password=password,
				  csrfmiddlewaretoken=session.cookies['csrftoken'],next=next_url)
	r = session.post(login_url, data=form_data, cookies=dict(), headers=dict(Referer=login_url))

	# check if request executed successfully?
	print r.status_code
	
	cookies = session.cookies
	print cookies

	if not os.path.exists(home +"/.hue_cli/"):
		os.makedirs(home +"/.hue_cli/")
	save_cookies(cookies, home +"/.hue_cli/session")
	headers = session.headers

	r=session.get(hueURL +'/metastore/databases/default/metadata', 
	cookies=session.cookies, headers=session.headers)
	print r.status_code

	# check metadata output
	print r.text

def get_session():
	if not os.path.exists(home + '/.hue_cli/session'):
		print("error. No session available. You should login first")
		sys.exit(1)
	s = load_cookies(home + '/.hue_cli/session')
	return s