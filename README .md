
# GOVERNMENT STALL RENTAL SYSTEM

Overview
The Government Stall Rental System is a web-based application designed to streamline the process of renting market stalls. This system enables administrators to manage stall inventory, rental agreements, payments, and tenant information. This system also provides an easy-to-use UI for tenants to apply for and renew stall.


## Features

- Stall location 
- Live tenant attendance system
- add, edit, delete stall details
- make announcements
- view payment records
- Manage tenant 
- Tenant profile
- Payment methods
- AI chatbot
- Feedback system 


## Tech Stack

- Frontend: tkinter, customtkinter
- Backend: Python, HTML
- Database: SQLite


## Installation
1. Download the whole project from GitHub.
2. After opening the project in PyCharm, please make sure that each of these Python Packages below is installed:
	DateTime	
	Flask
	Flask-Cors	
	Jinja2
	Markdown	
	MarkupSafe
	PySocks
	Pygments
	Werkzeug
	absl-py	
	astunparse	
	attrs	
	babel	
	bcrypt	
	beautifulsoup4	
	blinker	
	branca	
	certifi	
	cffi	
	chardet	
	charset-normalizer	
	click	
	cmake	
	colorama	
	comtypes	
	contourpy	
	cryptography	
	customtkinter	
	cycler	
	darkdetect	
	decorator	
	deepface	
	face_recognition_models	
	filelock	
	fire	
	flask-sock	
	flatbuffers	
	folium	
	fonttools	
	fpdf	
	future	
	gast	
	gdown	
	geocoder	
	google-pasta	
	grpcio	
	gunicorn	
	h11	
	h5py	
	idna
	itsdangerous	
	keras	
	kiwisolver	
	libclang	
	markdown-it-py	
	matplotlib	
	mdurl	
	ml-dtypes	
	mtcnn	
	namex	
	numpy	
	opencv-python
	opt-einsum	
	optree	
	outcome	
	packaging
	pandas	
	pillow	
	pip	
	protobuf	
	psutil	
	pyOpenSSL	
	pycparser	
	pyparsing	
	pyperclip	
	python-dateutil	
	python-dotenv	
	pytz	
	pywifi
	pywin32	
	qrcode	
	ratelim	
	reportlab	
	requests	
	retina-face	
	rich	
	scapy	
	selenium	
	setuptools	
	simple-websocket	
	six	
	sniffio	
	sortedcontainers	
	soupsieve	
	sseclient	
	tensorboard	
	tensorboard-data-server	
	tensorflow	
	tensorflow-intel	
	termcolor	
	tf_keras	
	tkcalendar	
	tkintermapview	
	tqdm	
	trio	
	trio-websocket
	typing_extensions	
	tzdata	
	urllib3	
	webdriver-manager	
	websocket-client	
	websockets	
	wheel	
	wrapt	
	wsproto	
	xyzservices	
	zope.interface	

3. Try running the file "create_db.py". If it says "An error occurred: table admin already exists", which means the database is already existed.
4. Run the file "tenant_signup_with_face_setup.py" for tenant, and "admin_signup.py" for admin. 

PS note: - make sure that all the files are in the same directory.
	 - make sure that "tenant_signup_with_face_setup.py" or "admin_signup.py" is running one at a time. DON'T RUN BOTH FILES TOGETHER because there will be a issue for the camera if you do that.

## Usage/Examples

- Admin signs-up / log in the account.
- Admin can choose manage user, manage stall, send notification, payment records, pending approval, view problem from the dashboard.
- Admin can view tenants (total tenants, problematic tenants).
- Admin can add, edit, delete stalls.
- Admin can view payment records.
- Admin can view feedbacks from tenants.
- Admin can approve / reject tenant rental applications.
- Tenants sign-up / log in the account.
- Tenant can update personal profile.
- Tenant can view available stalls. 
- Tenant can pay through 3 different methods.
- Tenant can generate receipt after payment. 
- Tenant can view announcement from admin.
- Tenant can give feedback. 



If you encountered any questions, please feel free to contact any of our group team members.
