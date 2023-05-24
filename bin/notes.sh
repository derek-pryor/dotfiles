#!/bin/bash

# References used to create this script
# Getopts example: https://stackoverflow.com/a/52674277
# Select menu: https://askubuntu.com/a/55901
# Uppercasing words: https://stackoverflow.com/a/2453056
# https://www.baeldung.com/linux/reading-output-into-array

PAGER="-p"

cd ~/notes

printHelp() {
    cat << EOF
Usage: $0 <ls|new|view|items> [-p] [note name]

If a note name is required but not given the user will be prompted to select from a list of existing note names

Action:
  ls    List all of the note names
  new   Create a new note with the given name
  view  View all of the notes with the given name
  items View all of the actions items from notes with the given name

Options:
-p		Display files using a pager
EOF
}

getNotes() {
    readarray -t notes < <(ls *.md | cut -d'-' -f2- | sed -e 's/\.md//' -e 's/-/ /g' -e 's/\<./\U&/g' | sort | uniq)
}

getNote() {
    if [ $# -eq 1 ] ; then
	getNotes
	#note=$(gum choose --header "Which note?" "${notes[@]}")
	note=$(for note in "${notes[@]}"; do echo $note; done | gum filter --header "Which note?")
	#note=$(for note in "${notes[@]}"; do echo $note; done | fzf)
	if [ "$note" = "" ] ; then
	    echo "No note selected"
	    exit 2
	fi
	note=$(echo "${note}" | sed -e 's/ /-/g' -e 's/\<./\L&/g')
    else
	shift # remove the sub-command
	note=$(echo "${@}" | sed -e 's/ /-/g' -e 's/\<./\L&/g')
    fi
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

printNote() {
	(
	for file in $(ls *-${note}.md); do
	    printDated $file
	done
    ) | glow $PAGER -
}

printItems() {
(
ls *-${note}.md | while read file ; do
    ts=$(echo $file | cut -f1 -d'-' | date -d - '+%A %B %d %Y')
    headers=()
    headersPrinted=false
    headersPrintIdx=0
    grep -e "\[ \]" -e "\#" $file | while read line ; do
	prefix=$(echo "$line" | cut -d' ' -f1)
        if [ "$prefix" = "-" ] ; then
	    if [ "$headersPrinted" = false ] ; then
		if [ $headersPrintIdx == 0 ] ; then
		    echo
		fi

		for ((i=$headersPrintIdx; i<${#headers[@]}; i++)) ; do
		    if (( $i == 0 )) ; then
			if [ "${note}" = "*" ] ; then
			    echo "${headers[$i]} ($file)"
			else
			    echo "${headers[$i]} ($ts)"
			fi
		    else
			echo ${headers[$i]}
		    fi
		done
		headersPrinted=true
		headersPrintIdx=${#headers[@]}
	    fi
	    printf "%s\n" "$line"
	else
	    if (( ${#prefix} > ${#headers[@]} )) ; then
		headers+=("$line")
		headersPrinted=false
	    else
		while (( ${#prefix} <= ${#headers[@]} )) ; do
		    unset headers[${#headers[@]}-1]
		done
		headersPrintIdx=${#headers[@]}
		headers+=("$line")
		headersPrinted=false
	    fi
	fi
    done
done
) | glow $PAGER -
}

case "$0" in
    *notes.sh)
	case "$1" in
	    ls)
		getNotes
		for note in "${notes[@]}"; do
		    echo $note
		done
		;;
	    new)
		today=$(date +%Y%m%d)
		getNote "${@}"
		fileName="${today}-${note}.md"

		exec ${EDITOR:-vim} $fileName
		;;
	    view)
		getNote "${@}"
		printNote
		;;
	    items)
		if [ "$2" = "--all" ] ; then
		    note="*"
		else
		    getNote "${@}"
		fi
		printItems
		;;
	    *)
		echo "Unknown command: $1"
		printHelp
		exit 1
		;;
	esac
	;;
esac
