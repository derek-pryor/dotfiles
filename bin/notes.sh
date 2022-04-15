#!/bin/bash

# References used to create this script
# Getopts example: https://stackoverflow.com/a/52674277
# Select menu: https://askubuntu.com/a/55901
# Uppercasing words: https://stackoverflow.com/a/2453056
# https://www.baeldung.com/linux/reading-output-into-array

PAGER=""

cd ~/notes

printHelp() {
    cat << EOF
Usage: $0 [-p]
View all related markdown notes together

-p		Display files using a pager
EOF
}

printDated() {
	file=$1
	ts=$(echo $file | cut -f1 -d'-' | date -d - '+%A %B %d %Y')

	line=$(head -n 1 $file)
	if [[ $line == "# "* ]]; then
	    echo "${line} (${ts})"
	else
	    echo "# ${ts}"
	    echo "${line}"
	fi

	tail -n +2 $file # all lines starting at the second line
}

getNote() {
    readarray -t notes < <(ls *.md | cut -d'-' -f2- | sed -e 's/\.md//' -e 's/-/ /g' -e 's/\<./\U&/g' | sort | uniq)

    echo "Which notes to view?"
    COLUMNS=12
    PS3="Pick an option:"
    select note in "${notes[@]}" "Quit"; do
	if [[ "$note" == "Quit" ]]; then
	    exit 0
	fi

	(
	for file in $(ls *$(echo "-${note}.md" | sed -e 's/ /-/g' -e 's/\<./\L&/g')); do
	    printDated $file
	done
    ) | glow $PAGER -

	break
    done
}

while getopts "hp" option; do
    case "${option}" in
	h)
	    printHelp
	    exit 0
	    ;;
	p)
	    PAGER="-p"
	    ;;
	*)
	    echo "Unknown Option: ${option}"
	    printHelp
	    exit 1
	    ;;
    esac
done

getNote
