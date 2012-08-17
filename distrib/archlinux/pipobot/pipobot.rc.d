#!/bin/bash

daemon_name=pipobot
PID_FILE=/var/run/$daemon_name.pid

. /etc/rc.conf
. /etc/rc.d/functions
. /etc/conf.d/$daemon_name.conf

get_pid() {
    if [ -f $PID_FILE ]; then
        /bin/kill -0 $(cat $PID_FILE)
        if [ $? == 0 ]; then
            cat $PID_FILE
        fi
    fi
}
case "$1" in
	start)
		stat_busy "Starting $daemon_name daemon"

		PID=$(get_pid)
		if [[ -z $PID ]]; then
			[[ -f $PID_FILE ]] &&
				rm -f $PID_FILE
		# RUN
		$daemon_name -b $CONFIG_FILE --pid $PID_FILE
		#
		if [[ $? -gt 0 ]]; then
			stat_fail
			exit 1
		else
			add_daemon $daemon_name
			stat_done
		fi
		else
			stat_fail
			exit 1
		fi
		;;

	stop)
		stat_busy "Stopping $daemon_name daemon"
		PID=$(get_pid)
		# KILL
		[[ -n $PID ]] && kill $PID &> /dev/null
		#
		if [[ $? -gt 0 ]]; then
			stat_fail
			exit 1
		else
			rm -f $PID_FILE &> /dev/null
			rm_daemon $daemon_name
			stat_done
		fi
		;;

	restart)
		$0 stop
		sleep 3
		$0 start
		;;

	status)
		stat_busy "Checking $daemon_name status";
		ck_status $daemon_name
		;;

	*)
		echo "usage: $0 {start|stop|restart|status}"
esac

exit 0

# vim:set ts=2 sw=2 et:
