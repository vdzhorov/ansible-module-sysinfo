#!/usr/bin/python

import subprocess
import distutils.spawn
from os.path import exists
import psutil
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: sysinfo

version_added: "0.1"

short_description: Get system information.

description: Module which gathers summarized information about the underlying system.

options:
    field:
        description: Filter system information by field. Possible values are distro, board
                    kernel, cpu, mem_total, mem_free, mem_available, disk_total, disk_used, disk_free.
                    If none values are passed, the default is to show all information.
        required: false
        type: str

author:
    - Valentin Dzhorov(@vdzhorov)
'''

EXAMPLES = r'''
- name: Get all system information
  sysinfo:

- name: Get board information only
  sysinfo:
    field: board
'''

RETURN = r'''
system_information:
    description: The dictionary which holds all the system information
    type: dict
    returned: always
    sample: {
        "changed": false,
        "system_information": "disk_free: 10 GB"
    }
'''


def cmd(command, in_shell=True):
    output = subprocess.check_output(command, shell=in_shell)
    return output.decode().strip()


def exec_exists(executable):
    if distutils.spawn.find_executable(executable):
        return True
    else:
        return False


class HardwareInfo:
    @staticmethod
    def get_cpus():
        return cmd("grep 'processor' /proc/cpuinfo | wc -l")

    @staticmethod
    def get_mem_total():
        return round(int(cmd(
            "grep 'MemTotal' /proc/meminfo | awk '{ print $2 }'"
        ))/1024)

    @staticmethod
    def get_mem_free():
        return round(int(cmd(
            "grep 'MemFree' /proc/meminfo | awk '{ print $2 }'"
        ))/1024)

    @staticmethod
    def get_mem_available():
        return round(int(cmd(
            "grep 'MemAvailable' /proc/meminfo | awk '{ print $2 }'"
        )) / 1024)

    @staticmethod
    def distro():
        distro = ""
        if exec_exists("lsb_release"):
            distro = cmd("lsb_release -sirc").replace("\n", " ")
        elif exists("/etc/redhat-release"):
            distro = cmd("cat /etc/redhat-release")
        return distro

    @staticmethod
    def kernel():
        return cmd("uname -r")

    @staticmethod
    def baseboard():
        vendor = "None"
        board = "None"
        chipset = "None"
        if exists("/sys/devices/virtual/dmi/id/board_vendor"):
            vendor = cmd("cat /sys/devices/virtual/dmi/id/board_vendor")
        elif exists("/sys/devices/virtual/dmi/id/sys_vendor"):
            vendor = cmd("cat /sys/devices/virtual/dmi/id/sys_vendor")

        if exists("/sys/devices/virtual/dmi/id/board_name"):
            board = cmd("cat /sys/devices/virtual/dmi/id/board_name")
        elif exists("/sys/devices/virtual/dmi/id/chassis_vendor"):
            board = cmd("cat /sys/devices/virtual/dmi/id/chassis_vendor")

        if exec_exists("lspci"):
            chipset = cmd("lspci -s 0:0.0 -xxx | head -1 | cut -d ' ' -f2- | cut -d ':' -f2-")
        return vendor + " " + board + ", " + chipset

    @staticmethod
    def disks():
        return psutil.disk_usage('/')


def run_module():

    module_args = dict(
        field=dict(type="str", required=False, default="all")
    )

    result = dict(
        changed=False,
        system_information=""
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    info = HardwareInfo()

    try:
        disk_total = str(round(int(info.disks().total / 1024 / 1024 / 1024)))
        disk_used = str(round(int(info.disks().used / 1024 / 1024 / 1024)))
        disk_free = str(round(int(info.disks().free / 1024 / 1024 / 1024)))
    except ImportError:
        disk_total = "None"
        disk_used = "None"
        disk_free = "None"

    all_info = {
        "distro": info.distro(),
        "board": info.baseboard(),
        "kernel": info.kernel(),
        "cpu": info.get_cpus(),
        "mem_total": str(info.get_mem_total()) + " MB",
        "mem_free": str(info.get_mem_free()) + " MB",
        "mem_available": str(info.get_mem_available()) + " MB",
        "disk_total": disk_total + " GB",
        "disk_used": disk_used + " GB",
        "disk_free": disk_free + " GB"
    }

    if module.params['field'] == "distro":
        result['system_information'] = "distro: " + all_info['distro']
    elif module.params['field'] == "board":
        result['system_information'] = "board: " + all_info['board']
    elif module.params['field'] == "kernel":
        result['system_information'] = "kernel: " + all_info['kernel']
    elif module.params['field'] == "cpu":
        result['system_information'] = "cpu: " + all_info['cpu']
    elif module.params['field'] == "mem_total":
        result['system_information'] = "mem_total: " + all_info['mem_total']
    elif module.params['field'] == "mem_free":
        result['system_information'] = "mem_free: " + all_info['mem_free']
    elif module.params['field'] == "mem_available":
        result['system_information'] = "mem_available: " + all_info['mem_available']
    elif module.params['field'] == "disk_total":
        result['system_information'] = "disk_total: " + all_info['disk_total']
    elif module.params['field'] == "disk_used":
        result['system_information'] = "disk_used: " + all_info['disk_used']
    elif module.params['field'] == "disk_free":
        result['system_information'] = "disk_free: " + all_info['disk_free']
    else:
        result['system_information'] = all_info

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
