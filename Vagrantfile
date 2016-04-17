# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty32"

  # config.vm.network "forwarded_port", guest: 8000, host: 8000

  # it is here for better performance
  config.vm.network "private_network", type: "dhcp"
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["rw", "vers=3", "tcp", "fsc" ,"actimeo=2"]

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end

  config.vm.provision :shell, path: "bin/vagrant/install.sh"
end