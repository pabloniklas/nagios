# nagios

This is a repository for plugins for the Nagios Monitoring System.
All this work is under the GNU License.

## used_space.py

### Description
Based on a work of http://stackoverflow.com/users/376587/giampaolo-rodol%c3%a0
It gives the occupied space in any filesystem, or all the mounted filesystems in the system.

### Usage

```bash
./used_space.py -w <warning_level> -c <critical_level>
```

Example:
 
```bash
./used_space.py -w 80 -c 10
```

or 

```bash
./used_space.py -w <warning_level> -c <critical_level> -p <mount point>
```

Example 

```bash
./used_space.py -w 80 -c 10 -p /
```

