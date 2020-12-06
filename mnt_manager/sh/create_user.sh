#!/bin/bash
# set -x

create_user(){
	if [ -n "$2" ]; then
		useradd -m -p "$pass" -s "/bin/bash" $1
		echo "$1:$2" | chpasswd
	else
		useradd $1
		echo "User has no password."
	fi
}

if [ -z "$1" ]; then
	echo "No arguments" >&2
	exit 1
fi

if [[ ! $( grep -E "^$1:" /etc/passwd | wc -l ) -ge 1 ]]; then
	if [[ $(id -u) -eq 0 ]]; then
		create_user $1 $2 
	else
		echo "No permission" >&2
		exit 1
	fi
else
	echo "User exitsts" >&2
	exit 1
fi

echo "The user has been created succesfful"
