#
# Regular cron jobs for the foam package
#
0 *	* * *	www-data [ -x /opt/ofelia/ofam/bin/expire ] && /opt/ofelia/ofam/bin/expire
40 0,6,12,18 * * *  www-data [ -x /opt/ofelia/ofam/bin/expire-emails ] && /opt/ofelia/ofam/bin/expire-emails
0 3 * * * www-data [ -x /opt/ofelia/ofam/bin/daily-queue ] && /opt/ofelia/ofam/bin/daily-queue
