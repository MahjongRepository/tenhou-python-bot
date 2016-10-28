# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/xenial64"

  # it is here for better performance
  config.vm.network "private_network", type: "dhcp"
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["rw", "vers=3", "tcp", "fsc" ,"actimeo=2"]

  config.vm.provider "virtualbox" do |v|
    v.memory = 512
  end

  config.vm.provision :shell, path: "bin/vagrant/install.sh"
end