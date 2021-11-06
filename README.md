# Ansible module sysinfo

## Description

This module is used for gathering synthesized system information.
I know that there are other ways to get information via built-in
Ansible modules, however this module can be extended if needed be.

## Installation

Place the module inside the "library" path.

## Requirements

- ansible
- python psutil module
- lspci (optional)

## Example tasks

```yaml
- name: Get all system information
  sysinfo:
```

```yaml
- name: Get board information only
  sysinfo:
    field: board
 ```

## Options

```yaml
options:
    field:
        description: Filter system information by field. Possible values are distro, board
                    kernel, cpu, mem_total, mem_free, mem_available, disk_total, disk_used, disk_free.
                    If none values are passed, the default is to show all information.
        required: false
        type: str
```
