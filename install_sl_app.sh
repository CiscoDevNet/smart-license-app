#!/usr/bin/env bash
#set -x #To debug remove the first #

echo -e "\n"
echo "############################################"
echo "Starting Smart Licensing App Installation..."
echo "############################################"

binaries_mac="git python3 yarn"
binaries_ubuntu="curl git python3 virtualenv python3-pip "
packages="flask flask-Cors flask-JWT flask-RESTful flask-SQLAlchemy netmiko numpy pandas pyOpenSSL pyping pyYAML requests tftpy"

if [ `uname -s` == 'Linux' ] 
then
    OS="ubuntu"
else 
    OS="mac"
fi

function execute_command()
{
    $*
    if [ $? -ne 0 ]
    then
        echo -e "\n"
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo "ERROR in executing the command "$*". Pls correct the error."
        echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        echo -e "\n"
        exit
    fi
}

function install_brew()
{
    echo -e "\n"
    echo "==>> Installing homebrew..."
    echo -e "\n"
    execute_command /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    echo "==>> Update homebrew recipes..."
    execute_command brew update
}

function install_binaries_mac()
{
    xcode-select --install
    install_brew
    for i in $binaries_mac
    do
        echo -e "\n"
        echo "==>> Installing the package "$i"..."
        echo "------------------------------------------"
        execute_command brew install $i
        echo "------------------------------------------"
    done
    echo "==>> Installing the package pip3..."
    echo "------------------------------------------"
    execute_command curl -O https://bootstrap.pypa.io/get-pip.py
    execute_command sudo python3 get-pip.py
    echo -e "\n"
    echo "------------------------------------------"
    echo "Installing virtual env..."
    echo "------------------------------------------"
    execute_command sudo -H pip3 install virtualenv
    echo "------------------------------------------"
}
function install_binaries_ubuntu()
{
    for i in $binaries_ubuntu
    do
        echo -e "\n"
        echo "==>> Installing the package "$i"..."
        echo "------------------------------------------"
        sudo apt-get install -y $i
        sudo apt-get upgrade -y $i
        echo "------------------------------------------"
    done
    echo "==>> Installing yarn"
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install -y yarn
}

function install_pip_packages()
{
    for i in $*
    do
        echo -e "\n"
        echo "==>> Installing the package "$i"..."
        echo "------------------------------------------"
        execute_command pip install $i
        echo "------------------------------------------"
    done
    echo -e "\n"
}

VIRTUALENV_PATH="./venv/"
INSTALL_PATH="."
INSTALL_PACKAGES=0
CREATE_VENV=0
BUILD_UI=0
LOCATION_OF_ZIP=""
LOCATION_OF_ZIP_PROVIDED=0
LOCATION_OF_APP="smart-license-app"

POSITIONAL=()
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        -c)
            CREATE_VENV=1
            shift
            ;;
        -i)
            INSTALL_PACKAGES=1
            shift
            ;;
        -u)
            BUILD_UI=1
            shift
            ;;
        -v)
            VIRTUALENV_PATH="$2"
            shift
            shift
            ;;
        -l)
            INSTALL_PATH="$2"
            shift
            shift
            ;;
        -h)
            echo -e "\n"
            echo "==>> Usage ./install_sl_app.sh [-c -i -u -v <virtual_environment direcotry> -l <installation dir>]"
            echo -e "\n"
            echo "-c option should be used if you want to create a new Virtual Environment (If you want to use existing Virtual Environment then provide location with -v option)"
            echo "-i option should be used if you want to install packages required by Smart Licensing App (If you already have packages in you environment then you can skip this option)"
            echo "-u option should be used if you want to use UI provided by Smart Licensing App (Skip this option if you just want to use Smart Licensing App backend REST apis)"
            echo "-v option is mandatory. Provide absolute path where you want to install Virtual Environment (OR Provide absolute path to existing Virtual Environment)"
            echo "-l option is mandatory. Provide absolute path to Smart Licensing app installation directory"
	    echo "-z option is mandatory. Location of the zip file where the app is downloaded"
            exit
            ;;
        -z)
	    LOCATION_OF_ZIP="$2"
	    LOCATION_OF_ZIP_PROVIDED=1
	    shift;
	    shift;
	    ;;
        *)
            POSITIONAL+=("$1")
            shift
            ;;
    esac
done

echo -e "\n"
echo "==>> Using Virtual Environment directory as "$VIRTUALENV_PATH" and installation of binaries at:  "$INSTALL_PATH

if [ $INSTALL_PACKAGES -eq 1 ] 
then
echo install_binaries_$OS
    install_binaries_$OS 
fi

if [ $CREATE_VENV -eq 1 ] 
then
echo -e "\n"
echo "==>> Creating a Virtual Environment (To run Smart Licensing App) at: "$VIRTUALENV_PATH
    python_binary=`which python3`
    execute_command virtualenv $VIRTUALENV_PATH/ -p python3
    execute_command source $VIRTUALENV_PATH/bin/activate
    execute_command install_pip_packages $packages
else
    execute_command source $VIRTUALENV_PATH/bin/activate
fi

cd $INSTALL_PATH
if [ $LOCATION_OF_ZIP_PROVIDED -eq 0 ]
then
    execute_command git clone https://github.com/CiscoDevNet/smart-license-app.git
else
    unzip $LOCATION_OF_ZIP
    LOCATION_OF_APP="smart-license-app-master"
fi

if [ $BUILD_UI -eq 1 ]
then
echo -e "\n"
echo "==>> Building UI for Smart Licensing App..."
    execute_command cd $LOCATION_OF_APP/frontend
    execute_command yarn install
    execute_command yarn build
    cd ..
    cd ..
fi

echo -e "\n"
echo "==>> Starting Smart Licensing App...\n"
echo -e "\n"
export PYTHONUNBUFFERED=1
execute_command cd $LOCATION_OF_APP
execute_command nohup python slta_resful.py &
echo "###########################################################"
echo "#### SUCCESS: Smart Licensing App has started with the pid: "$!
echo "###########################################################"
echo -e "\n"
echo "==>> Please go to browser and type https://0.0.0.0:5000 to start using Smart Licensing App..."
echo -e "\n"
echo "==>> Log messages can be found in nohup.out file in install dir <<=="
echo -e "\n"
echo "==>> Press ENTER <<=="

