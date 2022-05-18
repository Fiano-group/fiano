#!bin/bash
clear
today=$(date +"%Y-%m-%d")
PWD=$(pwd)
path2db=$(find . -name 'users.db')
while true; do
	if [[ -f "$path2db" ]]; then
		echo "********************** ANALYSIS TABLE ************************"
		echo "SELECT * FROM analysis" | sqlite3 $path2db
	else
		echo "There is not users.db file"
	fi
	sleep 1.7
	clear
done

