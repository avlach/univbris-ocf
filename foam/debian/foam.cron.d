#
# Regular cron jobs for the foam package
#
0 *	* * *	www-data [ -x /opt/foam/bin/expire ] && /opt/foam/bin/expire
40 0,6,12,18 * * *  www-data [ -x /opt/foam/bin/expire-emails ] && /opt/foam/bin/expire-emails
0 3 * * * www-data [ -x /opt/foam/bin/daily-queue ] && /opt/foam/bin/daily-queue
