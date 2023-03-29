set -e
# warn if nohz kernel option isn't set
if ! $(cat /proc/cmdline | grep nohz); then
  echo "Warning: nohz kernel option is not set. This can impact benchmarking resuls"
fi
# disable SMT
echo off > /sys/devices/system/cpu/smt/control
# Configure cpuset to isolate cores from the scheduler
# based on: https://www.suse.com/c/cpu-isolation-practical-example-part-5/
# TODO(boomanaiden154): make this script more adaptable rather than specific
# to one of my systems.
# TODO(boomanaiden154): actually make this script do things at runtime
# instead of just checking for the kernel flags. As far as I can tell, cgroups
# v2 removes support for configuring the scheduler.
# warn if isolcpus isn't set
if ! $(cat /proc/cmdline | grep isolcpus); then
  echo "Warning: isolcpus kernel option is not set."
fi
