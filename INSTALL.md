# Install instructions

## Vim 8+

* `ln -s /path/to/dotfiles/vim ~/.vim`
* `ln -s /path/to/dotfiles/vim/vimrc ~/.vimrc`
* `vim -u NONE -c "helptags ~/.vim/pack/dist/start/vim-airline/doc" -c q`
* `vim -u NONE -c "helptags ~/.vim/pack/dist/start/vim-airline-themes/doc" -c q`
* `vim -u NONE -c "helptags ~/.vim/pack/plugins/start/vim-go/doc" -c q`
* `vim -u NONE -c "helptags ~/.vim/pack/tpope/start/fugitive/doc" -c q`
* `vim -u NONE -c "helptags ~/.vim/pack/vendor/start/nerdtree/doc" -c q`
* `vim -u NONE -c "GoInstallBinaries" -c q`
