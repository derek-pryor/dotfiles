vimdiff <(jq --sort-keys . $1) <(jq --sort-keys . $2)
