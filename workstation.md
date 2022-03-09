Install pass (`yum install pass`)
Install pass otp (`dnf install pass-otp`)
Install gh cli (https://github.com/cli/cli/blob/trunk/docs/install_linux.md)
Install xclip

Create pass key (`gpg --full-generate-key`)
Initialize pass (https://git.zx2c4.com/password-store/about/#EXTENDED%20GIT%20EXAMPLE)

Get OTP URI
Add pass otp (`pass otp insert <pass-name>` and provide the URI)

Add pass kerberos password

Create gh signature key (`gpg --full-generate-key` just created signing RSA key)
Export key (`gpg --armor --export <keyid>`)
Under github settings add the GPG public key
Configure git to know about the key (`gpg --list-secret-keys --keyid-format=long`, take the key-id after the `sec    rsa4096/` part, `git config --global user.signingkey <key-id>`)
Configure git to automatically sign (`git config --global commit.gpgsign true`)


Authenticated Github CLI (`gh auth login`)
Set editor (`gh config set editor vim`)

`ln -s ~/repositories/dotfiles/bin ~/.local/bin`

Download slack-term and put into ~/.local/bin

ln -s ~/repositories/dotfiles/tmux ~/.tmux
ln -s ~/repositories/dotfiles/tmux/tmux.conf ~/.tmux.conf
ln -s ~/repositories/dotfiles/vim ~/.vim
ln -s ~/repositories/dotfiles/vim/vimrc ~/.vimrc
ln -s ~/repositories/dotfiles/xmobar/xmobarrc ~/.xmobarrc
ln -s ~/repositories/dotfiles/xmonad/xmonad.hs ~/.xmonad/xmonad.hs


pvaucontrol
gnome-control-center
bluetoothctl

To find the firewall service for a given port `grep -r <port-number> /usr/lib/firewalld/services`
