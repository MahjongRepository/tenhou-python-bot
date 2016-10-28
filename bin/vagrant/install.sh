#!/bin/sh -e

# we need to do it, to have latest version of packages
sudo apt-get update
sudo apt-get -y upgrade

sudo apt-get -y install python-pip
sudo apt-get -y install python-virtualenv

# install python libraries
virtualenv --python=python3.5 /home/ubuntu/env/
/home/ubuntu/env/bin/pip install --upgrade pip
/home/ubuntu/env/bin/pip install -r /vagrant/project/requirements.txt

# activate virtualenv on login and go to working dir
sh -c "echo 'source /home/ubuntu/env/bin/activate' >> /home/ubuntu/.profile"
sh -c "echo 'cd /vagrant/project' >> /home/ubuntu/.profile"