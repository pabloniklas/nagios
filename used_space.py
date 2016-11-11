#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Occupied space in filesystems.
# Based on a work of Giampaolo Rodol
# http://stackoverflow.com/users/376587/giampaolo-rodol%c3%a0
#
# 20161110 - PSRN - Initial Version.
#

import os
import getopt
import sys
from collections import namedtuple

disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
usage_ntuple = namedtuple('usage', 'total used free percent')


def disk_partitions(all=False):
    """Return all mountd partitions as a nameduple.
    If all == False return phyisical partitions only.
    """
    phydevs = []
    f = open("/proc/filesystems", "r")
    for line in f:
        if not line.startswith("nodev"):
            phydevs.append(line.strip())

    retlist = []
    f = open('/etc/mtab', "r")
    for line in f:
        if not all and line.startswith('none'):
            continue
        fields = line.split()
        device = fields[0]
        mountpoint = fields[1]
        fstype = fields[2]
        if not all and fstype not in phydevs:
            continue
        if device == 'none':
            device = ''
        ntuple = disk_ntuple(device, mountpoint, fstype)
        retlist.append(ntuple)
    return retlist


def find_partition_by_name(name):

    for line in open("/etc/mtab").readlines():

        if name == line.split()[1].strip():

            device = line.split()[0].strip()
            mountpoint = line.split()[1].strip()
            fstype = line.split()[2].strip()

            return disk_ntuple(device, mountpoint, fstype)


def disk_usage(path):
    """Return disk usage associated with path."""
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0

    # NB: the percentage is -5% than what shown by df due to
    # reserved blocks that we are currently not considering:
    # http://goo.gl/sWGbH
    return usage_ntuple(total, used, free, round(percent, 1))


def printf(format, *args):
    sys.stdout.write(format % args)


def main(argv):
    warning = 80    # Defaults
    critical = 90   # Defaults

    fsarg = []

    try:
        opts, args = getopt.getopt(argv, "hw:c:p:", ["warning=", "critical=", "partition="])

    except getopt.GetoptError:
        print('used_space.py -w <warning_level> -c <critical_level>')
        sys.exit(3)

    for opt, arg in opts:
        if opt == '-h':
            print('used_space.py -w <warning_level> -c <critical_level>')
            sys.exit(3)
        elif opt in ("-w", "--warning"):
            warning = round(float(arg), 0)
        elif opt in ("-c", "--critical"):
            critical = round(float(arg), 0)
        elif opt in ("-p", "--partition"):
            fsarg.append(arg)

    rc_code = 0
    nro = 0

    if not fsarg:
        fslist = disk_partitions()
    else:
        fslist = []
        for fs in fsarg:
            fslist.append(find_partition_by_name(fs))

    printf("<!-- BEGIN Sensor Output -->")

    printf("<table border='0' width='100%%' class='status'>")

    printf("<tr>")
    printf("<th class='status'>Status</th>")
    printf("<th class='status'>Filesystem</th>")
    printf("<th class='status'>Occupied %%</th>")
    printf("</tr>")

    for part in fslist:
        percent = round(disk_usage(part.mountpoint).percent, 0)

        if (nro % 2) == 0:
            clase = "statusEven"
        else:
            clase = "statusOdd"

        if (percent >= warning) and (percent < critical):
            claseStatus, trc, texto = "statusBGWARNING", 1, "Warning"
        else:
            if percent >= critical:
                claseStatus, trc, texto = "statusBGCRITICAL", 2, "Critical"
            else:
                claseStatus, trc, texto = "statusOK", 0, "OK"

        printf("<tr>")
        printf("<td class='" + claseStatus + "'>" + texto + "</td>")
        printf("<td class='" + clase + "'>" + part.mountpoint + "</td>")
        printf("<td class='" + clase + "'>" + str(percent) + "</td>")
        printf("</tr>")

        if trc > rc_code:
            rc_code = trc

        nro += 1

    printf("</table>")
    printf("<!-- END Sensor Output -->")

    return rc_code


if __name__ == "__main__":
    rc = main(sys.argv[1:])

    sys.exit(rc)
