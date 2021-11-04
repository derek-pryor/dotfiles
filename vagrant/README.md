# Vagrant install instructions

## Fedora
1. Install the `vagrant` and `vagrant-libvirt` packages from the Fedora repos (`dnf install vagrant vagrant-libvirt`)
2. Place your user account in the `kvm` `qemu` and `libvirt` groups (edit `/etc/group`)
3. Install the NFS server on the host machine, for shared folder support (`dnf install nfs-utils`)
4. Enable the NFS server service
   - `systemctl enable rpc-bind`
   - `systemctl enable nfs-server`
   - `systemctl start rpc-bind`
   - `systemctl start nfs-server`
5. Allow libvirt VMs to access NFS in the firewall
   - `firewall-cmd --zone=libvirt --add-service=nfs3`
   - `firewall-cmd --zone=libvirt --add-service=rpc-bind`
   - `firewall-cmd --zone=libvirt --add-service=mountd`
