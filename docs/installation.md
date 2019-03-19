# Installation

This app can be installed on macOS, Linux and Windows operating systems. Installation instructions are given bellow for each operating systems.  

[Client ID and Secret & Get access to API Server - For all platform](#client-id-and-secret-get-access-to-api-server-for-all-platform)  
[Installation for macOS](#installation-for-macos)  
[Installation for Linux](#installation-for-linux)  
[Installation for Windows](#installation-for-windows)  
  
---  
## Client ID and Secret & Get access to API Server - For all platform
  
This is common for all platforms, must be performed once per application installation. User must have a CCO/Cisco.com account to register app instance.  
   

App connects to Cisco API Server to interact with Cisco Smart Software Management(CSSM). OAuth is enabled on Cisco API Server to provide access to Smart Licensing APIs. This app needs to get registered with API Server's Smart Licensing API App. 

1. To register and get client ID and secret, click on [Mulesoft - Cisco API Server](https://anypoint.mulesoft.com/apiplatform/apx/#/portals/organizations/1c92147b-332d-4f44-8c0e-ad3997b5e06d/apis/5418104/versions/102456/pages/309235)
  
    The link has instructions to register a new application.

    * Use 'Smart_Licensing_App' as the name of the app
    * Select only 'Resource Owner Grant' type from the options for OAuth grant type.

2. Once the app is registered with MuleSoft, user will get an email with application details, that includes client ID and secret, then **user needs to send an email to 'smart-operations@cisco.com' to get access to API server**. It may take **12-24 hrs** to get the access enabled after user gets an email confirmation.
  
    A 'config.yaml' file needs to created with the following content and place it in the user's home directory in the computer where the app is going to be installed.
    ```yaml
    api_keys:
        client_id: <client id from Mulesoft API Server application>
        client_secret: <client secret from Mulesoft API Server application>
    ```  


---
## Installation for macOS

**NOTE: If http & https proxies need to be set to get to internet for installing these packages, set it before continuing.**


### Section I

**Python3 & pip**

New MAC computers ship with Python3 pre-installed, execute the following command in a terminal to make sure that Python 3.6 or higher installed.

```sh
$ python3 --version
```

**NOTE: If Python 3.6 or higher is already installed, jump to Section II (Using 'virtualenv' section for installing virtual environment for Smart Licensing App).**

Python is not installed on Mac, follow steps listed below:

**1. Get Homebrew**
```sh 
$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
**2. Get Python3**
```sh 
$ brew install python3
```
**3. Get pip3 package**
```sh 
$ curl -O https://bootstrap.pypa.io/get-pip.py
```
**4. Install pip3**
```sh 
$ python3 get-pip.py
```
### Section II
**Using virtualenv**

Instead of installing packages needed for Smart Licensing app system-wide,  'virtualenv' is used in these instructions to create an isolated Python environment, then required packages are installed into this virtual environment.

**1. Install "virtualenv"**
```sh
$ sudo -H pip3 install virtualenv
```
**2. To make a virtual environment in which all other packages are going to be installed first create a directory in which environment is going to be set up.**
```sh
$ mkdir smart_license
$ cd smart_license
```
**3. Create a new directory "sl_venv" inside '<Machine name>:~ <user_id>\smart_license' with separate python interpreter by executing following command.**
```sh
$ virtualenv -p python3 sl_venv
```
**4. Activate virtualenv**
```sh
$ source sl_venv/bin/activate
(sl_venv) smart_license $
```
**NOTE: The (sl_venv) prefix to prompt in the last line indicates that newly created virtual environment is activated. All subsequently installed packages from this modified command prompt end up in the activated virtual environment. Virtual environment can be deactivated with command 'deactivate'.**

### Section III
**Install Packages**

Now required packages can be installed for running Smart Licensing App.
```sh
(sl_venv) smart_license $ pip3 install Flask
```
In a similar way, install following packages:

 1. Flask
 2. Flask-Cors
 3. Flask-JWT
 4. Flask-RESTful
 5. Flask-SQLAlchemy
 6. netmiko
 7. numpy
 8. pandas
 9. pyOpenSSL
10. pyping
11. pyYAML
12. requests
13. tftpy
14. schema

### Section IV

**App source code**

App source can be cloned from GitHub [smart-license-app](https://github.com/CiscoDevNet/smart-license-app) repository.
 
**Git Repository Clone**

Install Git on MAC (If Git is already installed, skip steps shown below and go to "To clone Smart Licensing App code" part)

1. Open a Terminal on the Mac. Now, type the command ('git --version') into the Terminal.
2. If git is not installed already, it will prompt to install it.
3. Read and agree to the Command Line Tools License Agreement and Git is ready to use.

**To clone Smart Licensing App code**
```sh
(sl_venv) smart_license $ git clone https://github.com/CiscoDevNet/smart-license-app.git
```
### Section V

**Build UI code**

UI needs to be built from the source before running the App. To build the UI code follow instructions below:

**1. Install Yarn**  
```sh
(sl_venv) smart_license $ brew install yarn
```
For more info about yarn: https://yarnpkg.com/lang/en/docs/install/#mac-stable
 
**2. Go to the UI source code directory**  
```sh
(sl_venv) smart_license $ cd smart-license-app/frontend
``` 
**3. Install node modules**  

Run the following command to install the required node modules:

```sh
(sl_venv) frontend $ yarn install
```
**4. Build the UI package**  

Run the following command to build the UI:

```sh
(sl_venv) frontend $ yarn build
```

UI package will be built in a new directory by name 'build'. Leave the files in 'build' directory as such, don’t modify anything, python app will pick the UI from the 'build' directory. Come out of 'frontend' directory.
```sh
(sl_venv) frontend $ cd ..
```
### Section VI

**Start Smart Licensing App**

Now it is ready to start Smart Licensing App. Start App using following commands.
```sh
(sl_venv) smart-license-app $ export PYTHONUNBUFFERED=1
(sl_venv) smart-license-app $ nohup python3 slta_resful.py &
```
**NOTE: After the App is started, open 'nohup.out' file to make sure that App is started successfully (i.e there are no error messages regarding missing packages etc.)**

**Using Smart Licensing App**

Open the browser and type: 'https://0.0.0.0:5000'  

OR, if trying to access GUI the remotely: 'https://<*FQDN or IP Address*>:5000'  

Browser will launch Smart Licensing App GUI.

---
## Installation for Linux

**NOTE: If http & https proxies need to be set to get to internet for installing these packages, set it before continuing.**
  
### Section I

**Python3 & pip**

New Ubuntu version ships with Python3 pre-installed, execute following command in terminal to make sure that Python 3.6 or higher installed.

```sh
$ python3 --version
```
User's computer might also have several versions of Python installed. The following command will help to get a list of all Python versions that are installed:

```sh
apt list --installed | grep python 
```
**NOTE: If Python 3.6 or higher installed, jump to Section II (Using 'virtualenv' section for installing virtual environment for Smart Licensing App).**

If Python is not installed already, follow steps listed below:

**1. The system repository index needs to be up to date so that the latest available version can be installed.**

```sh 
$ sudo apt-get update
``` 
**2. Install/Upgrade Python3**
```sh 
$ sudo apt-get install python3
$ sudo apt-get upgrade python3
```
**3. Before installing pip, a few prerequisites needs to be added that will help in setting up virtual space.**

```sh 
$ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
```

**4. Install pip3 if it is already not installed**

```sh 
$ sudo apt install python3-pip
```
### Section II

**Using virtualenv**

Instead of installing packages needed for Smart Licensing app system-wide, 'virtualenv' is used in these instructions to create an isolated Python environment, then required packages are installed into this virtual environment.

**1. Install "virtualenv"**

```sh
$ sudo -H pip3 install virtualenv
```

**2. To make a virtual environment in which all other packages are going to be installed first create a directory in which the virtual environment is going to be set up.**

```sh
$ mkdir smart_license
$ cd smart_license
```

**3. Create a new directory "sl_venv" inside 'smart_license' directory with separate python interpreter by executing following command.**

```sh
$ virtualenv -p python3 sl_venv
```

**4. Activate virtualenv**

```sh
$ source sl_venv/bin/activate
(sl_venv) smart_license $
```
**NOTE: The (sl_venv) prefix to prompt in the last line indicates that newly created virtual environment is activated. All subsequently installed packages from this modified command prompt end up in the activated virtual environment. Virtual environment can be deactivated with command 'deactivate'.**

### Section III

**Install Packages**

Now required packages can be installed for running Smart Licensing App.

```sh
(sl_venv) smart_license $ pip3 install Flask
```
In a similar way, install following packages:

 1. Flask
 2. Flask-Cors
 3. Flask-JWT
 4. Flask-RESTful
 5. Flask-SQLAlchemy
 6. netmiko
 7. numpy
 8. pandas
 9. pyOpenSSL
10. pyping
11. pyYAML
12. requests
13. tftpy
14. schema

### Section IV

**App source code**

App source can be cloned from GitHub [smart-license-app](https://github.com/CiscoDevNet/smart-license-app) repository.
 
**Git Repository Clone**

Install Git on Ubuntu (If Git is already installed, skip steps shown below and go to "Clone Smart Licensing App code" part)

**1. Open a Terminal, type the command ('git --version').**  

```sh
(sl_venv) smart_license $ git --version
```

**2. If git is not installed already, install it using command:**

```sh
(sl_venv) smart_license $ sudo apt install git
```

**3. Git installation can be confirmed by running the following command:**

```sh
(sl_venv) smart_license $ git --version
```

**To clone Smart Licensing App code**

```sh
(sl_venv) smart_license $ git clone https://github.com/CiscoDevNet/smart-license-app.git
```

### Section V

**Build UI code**  

UI needs to be built from the source code before running the App. To build the UI code follow instructions below:

**1. Install Yarn**  

```sh
(sl_venv) smart_license $ curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
(sl_venv) smart_license $ echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
(sl_venv) smart_license $ sudo apt-get update && sudo apt-get install yarn
```

For more info about yarn: https://yarnpkg.com/lang/en/docs/install
 
**2. Go to the UI source code directory**  

```sh
(sl_venv) smart_license $ cd smart-license-app/frontend
```
 
**3. Install node modules**  

Run the following command to install the required node modules:

```sh
(sl_venv) frontend $ yarn install
```
 
**4. Build the UI package**  

Run the following command to build the UI:

```sh
(sl_venv) frontend $ yarn build
```

UI package will be built in a new directory by name 'build'. Leave the files in 'build' directory as such, don’t modify anything, python app will pick the UI from the 'build' directory. Come out of 'frontend' directory.

```sh
(sl_venv) frontend $ cd ..
```

### Section VI

**Start Smart Licensing App**

Now it is ready to start Smart Licensing App. Start App using following commands.

```sh
(sl_venv) smart-license-app $ export PYTHONUNBUFFERED=1
(sl_venv) smart-license-app $ nohup python3 slta_resful.py &
```

**NOTE: After the app is started, open 'nohup.out' file and make sure that App is started successfully (i.e there are no error messages regarding missing packages etc.)**

**Using Smart Licensing App:**

Open the browser and type: 'https://0.0.0.0:5000'  

OR, if trying to access GUI the remotely: 'https://<*FQDN or IP Address*>:5000'  

Browser will launch Smart Licensing App GUI.
  
---
## Installation for Windows

**NOTE: If http & https proxies need to be set to get to internet for installing these packages, set it before continuing.**

### Section I

**Python3 & pip**

**NOTE: If Python 3.6 or higher is already installed, jump to 'virtualenv' section for installing virtual environment for Smart Licensing App.**

**Python 3.X**

1. Open up a browser and go to https://www.python.org. Scroll over to "Downloads" in the navigation bar. It will popup with most current version of Python3.
2. Click on Python3 button. It will download latest Python3 to the Downloads directory.
3. Once download is complete, click on the downloaded file and then click on Run button. Setup window will pop up. In setup window, select 'Add Python 3.X to PATH' (Adding Python 3.X to PATH will allow to launch it just by typing python in the command prompt) and click on install now.
4. Once installation is complete, open command prompt and execute 'path' command in it. Make sure that Python3.X and Python3.X/Scripts are present in the path.
5. Open a new Command Prompt window. Type 'python' in the command prompt and it will open up python shell. Type 'quit()' to come out of python shell.
6. Now type 'pip freeze' in the command prompt and that will show currently installed python packages (Which should be blank if there are no python packages installed)

### Section II

**virtualenv**

Instead of installing packages needed for Smart Licensing app system-wide, 'virtualenv' is used in these instructions to create an isolated Python environment, then required packages are installed into this virtual environment.

**1. Install 'virtualenv'**
```sh
C:\Users\<user_id> pip install virtualenv
```
**2. To make a virtual environment in which all other packages are going to be installed first create a directory in which the virtual environment is going to be set up.**
```sh
C:\Users\<user_id> mkdir smart_license
C:\Users\<user_id> cd smart_license
```
**3. Create a new directory 'sl_venv' inside 'C:\Users\<user_id>\smart_license' with separate python interpreter by executing following command**
```sh
C:\Users\<user_id>\smart_license> virtualenv sl_venv
```
**4. Activate virtualenv**
```sh
C:\Users\<user_id>\smart_license> sl_venv\Scripts\activate
(sl_venv) C:\Users\<user_id>\smart_license>
```
**NOTE:The (sl_venv) prefix to prompt in the last line indicates that newly created virtual environment is activated. All subsequently installed packages from this modified command prompt end up in the activated virtual environment. Virtual environment can be deactivated with command 'deactivate'.**

### Section III

**Packages**

Now required packages can be installed for running Smart Licensing App.
```sh
(sl_venv) C:\Users\<user_id>\smart_license> pip install Flask
```
**NOTE: Make sure computer is connected to internet for installing these packages.**

In a similar way, install following packages:  

 1. Flask
 2. Flask-Cors
 3. Flask-JWT
 4. Flask-RESTful
 5. Flask-SQLAlchemy
 6. netmiko
 7. numpy
 8. pandas
 9. pyOpenSSL
10. pyping
11. pyYAML
12. requests
13. tftpy
14. schema

### Section IV

**To get App source code**

App source can be cloned from GitHub [smart-license-app](https://github.com/CiscoDevNet/smart-license-app) repository.

**Git Repository**

Install Git on Windows (If Git is already installed, skip this section)

1. Go to the website: https://git-scm.com/download/win. If the download doesn’t start automatically, then click on 'click here to download automatically'.
2. Click on the .exe file.
3. Click on 'Run' when security warning is shown.
4. Go through the default installation process until 'Choosing the default editor used by Git' is shown. A choice of an editor could be chosen.
5. Choose 'Use Git and optional Unix Tools', if user likes to use Unix commands like 'ls' and 'cat'.
6. Choose 'Use Windows' default console window.
7. Click on 'Install'.
8. Click on 'Finish'.
9. Open command prompt and get started!

**To clone Smart Licensing App code**
```sh
(sl_venv) C:\Users\<user_id>\smart_license> git clone https://github.com/CiscoDevNet/smart-license-app.git
```
### Section V

**Build UI code**

UI needs to be built from the source code before running the App. To build the UI code, follow instruction below:

**1. Install Yarn**
 
Download the installer from the bellow URL and install it.
https://yarnpkg.com/lang/en/docs/install/#windows-stable
 
**2. Go to the UI source code directory**  
```sh
(sl_venv) C:\Users\<user_id>\smart_license> cd smart-license-app/frontend
```
 
**3. Install required node modules**  

Run the following command to install the required node modules:

```sh
(sl_venv) C:\Users\<user_id>\smart_license\smart-license-app\frontend> yarn install
```
**4. Build the UI package**  

Run the following command to build the UI
```sh
(sl_venv) C:\Users\<user_id>\smart_license\smart-license-app\frontend> yarn build
```
UI package will be built in a new directory by name 'build'. Leave the files in 'build' directory as such, don’t modify anything, python app will pick the UI from the 'build' directory. Come out of 'frontend' directory.
```sh
(sl_venv) C:\Users\<user_id>\smart_license\smart-license-app\frontend> cd ..
```
### Section VI

**Start Smart Licensing App**

Now it is ready to start Smart Licensing App. Start App using following commands.
```sh
(sl_venv) C:\Users\<user_id>\smart_license> cd smart-license-app
(sl_venv) C:\Users\<user_id>\smart_license\smart-license-app> start \min python slta_resful.py
```
NOTE: After the App is started, check console window to make sure that App is started successfully (i.e there are no error messages regarding missing packages etc.)  

**Using Smart Licensing App:**

Open the browser and type: 'https://0.0.0.0:5000'  

OR, if trying to access GUI the remotely: 'https://<*FQDN or IP Address*>:5000'  

Browser will launch Smart Licensing App GUI.


