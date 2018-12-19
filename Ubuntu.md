# Ubuntu specific updates

## Disable Network Manager
If using a desktop distribution / Network Manager

* Edit `/etc/network/interfaces`
  ```auto eth0
     iface eth0 inet dhcp
  ```
* Run `sudo systemctl stop NetworkManager.service`
* Run `sudo systemctl disable NetworkManager.service`

## Configure the default Login Manager
* Look at the valid DM in `/usr/share/xsessions/`
* Edit `/usr/share/lightdm/lightdm.conf.d/50-ubuntu.conf` and replace `ubuntu` with the desired value
