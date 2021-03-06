#!/usr/bin/env bash
# Absolute path to this script
SCRIPT=`realpath $0`
# Absolute directory this script is in
SCRIPTPATH=`dirname $SCRIPT`
echo $SCRIPT

which virtualenv > /dev/null
if [ "$?" -ne "0" ]; then
    echo "virtualenv not found!"
    echo -e "Please install virtualenv and retry Airtime installation.\n"
    exit 1
fi

#Check whether version of virtualenv is <= 1.4.8. If so exit install. 
BAD_VERSION="1.4.8"
VERSION=$(virtualenv --version)
NEWEST_VERSION=$(echo -e "$BAD_VERSION\n$VERSION\n" | sort -t '.' -g | tail -n 1)
echo -n "Ensuring python-virtualenv version > $BAD_VERSION..."

VIRTUAL_ENV_DIR="/usr/local/lib/airtime/airtime_virtualenv"
VIRTUAL_ENV_SHARE="/usr/local/share/python-virtualenv/"

if [ -d $VIRTUAL_ENV_DIR ]; then
    echo -e "\n*** Existing Airtime Virtualenv Found ***"
    rm -rf ${VIRTUAL_ENV_DIR}
    echo -e "\n*** Reinstalling Airtime Virtualenv ***"
fi

echo -e "\n*** Creating Virtualenv for Airtime ***"
EXTRAOPTION=$(virtualenv --help | grep extra-search-dir)

if [ "$?" -eq "0" ]; then
    virtualenv --extra-search-dir=${SCRIPTPATH}/3rd_party --no-site-package -p /usr/local/bin/python /usr/local/lib/airtime/airtime_virtualenv 2>/dev/null || exit 1
else
    # copy distribute-0.6.10.tar.gz to /usr/local/share/python-virtualenv/
    # this is due to the bug in virtualenv 1.4.9
    if [ -d "$VIRTUAL_ENV_SHARE" ]; then
        cp ${SCRIPTPATH}/3rd_party/distribute-0.6.10.tar.gz /usr/local/share/python-virtualenv/
    fi
    virtualenv --no-site-package -p /usr/local/bin/python /usr/local/lib/airtime/airtime_virtualenv 2>/dev/null || exit 1
fi

echo -e "\n*** Installing Python Libraries ***"
/usr/local/lib/airtime/airtime_virtualenv/bin/pip install ${SCRIPTPATH}/airtime_virtual_env.pybundle || true
/usr/local/lib/airtime/airtime_virtualenv/bin/pip install kombu
/usr/local/lib/airtime/airtime_virtualenv/bin/pip install mutagen
/usr/local/lib/airtime/airtime_virtualenv/bin/pip install pydispatcher
/usr/local/lib/airtime/airtime_virtualenv/bin/pip install pytz
/usr/local/lib/airtime/airtime_virtualenv/bin/pip install poster
cd ${SCRIPTPATH}/3rd_party/pyinotify
/usr/local/lib/airtime/airtime_virtualenv/bin/python setup.py install
cd ${SCRIPTPATH}
