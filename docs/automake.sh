#!/bin/bash


set -e  # Only for ls and inotifywait (to make sure files exist) ...

   # files to watch
THIS_SCRIPT=$(basename "$0")
WFILES=($(
find source/ -type f -not -name '.*' -not -name '#*' -not -name '*~';
find .. -type f -name '*.py' -not -name '#*') "$THIS_SCRIPT")

   # sub-directories to watch
WDIRS=($(find source/ -maxdepth 1 -mindepth 1 -type d -not -name ".*" ))

set +e  # Do *not* exit on a make error.  'Make' and other errors are handled.

# Workaround for Ubuntu's braindead notify policy: use a (two-line) modified
# version of libnotify to be able to have non-ten-second notification timeouts

# First, set a trap to kill our notify daemon before we exit
function kill_sub_program ( ) { kill $1; }
function cleanup ( ) {
	kill_sub_program $NOTIFY_PID

	exit
}
trap cleanup SIGINT SIGTERM

my_notify-osd.sh &> /dev/null &  # if it fails, no biggie, so after the +e
NOTIFY_PID=$!

PROJECT_TITLE="Temoa Project Documentation"
PASS_ICON="$(pwd)/notify.svg"
PASS_TIMEOUT=2000  # 2,000 milliseconds; appears to not work on Ubuntu 10.10
FAIL_TIMEOUT=5000  # 5,000 milliseconds; appears to not work on Ubuntu 10.10
RELOAD_TIMEOUT=1000 # 1,000 milliseconds; appears to not work on Ubuntu 10.10

PASS_MSG="Success!  Documentation generated successfully."
FAIL_MSG="Error generating documentation.  Doh!"
RELOAD_MSG="Automake script modified ... Reloading"
EXIT_MSG="Unable to re-execute automake script.  Exiting ..."

unset BASH
[[ -f ~/.terminal_colors ]] && . ~/.terminal_colors

# notify-send appears to need the full path to the icon.  Can't do relative.
# Sigh.
if [[ ! -f "$PASS_ICON" ]]; then
	PASS_ICON='/usr/share/icons/Humanity/emblems/24/emblem-ubuntuone-synchronized.svg'
	[[ ! -f "$PASS_ICON" ]] || PASS_ICON='info'
fi

if [[ ! -f "$FAIL_ICON" ]]; then
	FAIL_ICON='/usr/share/icons/Humanity/status/48/dialog-error.svg'
	[[ ! -f "$FAIL_ICON" ]] || FAIL_ICON='error'
fi

CMD="notify-send"
COMMON_ARGS='--urgency low --expire-time'
PASS_ARGS=($COMMON_ARGS "$PASS_TIMEOUT" '--icon' "$PASS_ICON" "$PROJECT_TITLE")
FAIL_ARGS=($COMMON_ARGS "$FAIL_TIMEOUT" '--icon' "$FAIL_ICON" "$PROJECT_TITLE")
RELOAD_ARGS=($COMMON_ARGS "$RELOAD_TIMEOUT" '--icon' 'info' "$PROJECT_TITLE")

INOTIFY_ARGS=(
  '-e' 'modify' '-e' 'move_self' '-e' 'delete_self'
  "${WFILES[@]}" '-qr' "${WDIRS[@]}"
)

if [[ $# == 0 ]]; then
	cat <<EOF
This script waits for changes to files or directories, executing a Makefile upon
an event.

Files currently observed:       ${WFILES[@]}
Directories currently observed: ${WDIRS[@]}

libnotify-bin commands (Growl-like notification message):

Success: $CMD ${PASS_ARGS[@]}
Failure: $CMD ${FAIL_ARGS[@]}

EOF
elif [[ $# == 1 && '-q' == "$1" ]]; then
	cat <<EOF
Files currently observed:       ${WFILES[@]}
Directories currently observed: ${WDIRS[@]}
EOF
fi


while [[ 1 ]]; do
	make "$@"

	if [[ $? = 0 ]]; then
		"$CMD" "${PASS_ARGS[@]}" "$PASS_MSG"
		echo -e "${LGREEN}Documenation successfully generated${FDEFAULT}"
	else
		"$CMD" "${FAIL_ARGS[@]}" "$FAIL_MSG"
		echo -e "${LRED}Documentation ${LBLUE}un${LRED}successfully generated${FDEFAULT}"
	fi

	echo -e "\n----\n"
	date

	echo 'Waiting for a file to be modified ...'
	R=$(inotifywait "${INOTIFY_ARGS[@]}")

	if [[ "$R" =~ $THIS_SCRIPT ]]; then
		echo -e "\t${LBLUE}Automake script modified ... Reloading${FDEFAULT}\n"
		echo -e "--------------------------------------------------------------\n"
		notify-send "${RELOAD_ARGS[@]}" "$RELOAD_MSG"

		sync
		sleep 1 # attempt to ensure $THIS_SCRIPT has been written/is not busy
		exec "$0" "$@"

		# Just to be safe, if exec fails for any reason, inform user, then exit.
		# This way they're aware of the issue.

		notify-send "${FAIL_ARGS[@]}" "$EXIT_MSG"
		echo -e "\n\n${LRED}Unable to re-execute automake script.  Exiting ...${FDEFAULT}"
		exit
	fi
done
