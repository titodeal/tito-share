#!/bin/bash
# set -x

create_user(){
	echo "= Creating user => $1"
	if [ -n "$2" ]; then
# 		pass=$(mkpasswd $2)
		echo "Creating Password User"
		useradd -p "$pass" -s "/bin/bash" $1
		echo "$1:$2" | chpasswd
	else
		useradd $1
		echo "User without password."
	fi
}

if [ -z "$1" ]; then
	echo "no arguments" >&2
	exit 1
fi

if [[ ! $( grep -E "^$1:" /etc/passwd | wc -l ) -ge 1 ]]; then
	if [[ $(id -u) -eq 0 ]]; then
		create_user $1 $2 
	else
		echo "== no permission" >&2
		exit 1
	fi
else
	echo "user exitst" >&2
	exit 1
fi

home_dir=$(grep -E "^$1" /etc/passwd | cut --delimiter=":" --fields=6)
if [[ ! -d "$home_dir" ]]; then
    echo "Creating home directory"
    mkdir "$home_dir"
    chown -R "$1":"$1" "$home_dir"
fi
echo "Creating Finish"
