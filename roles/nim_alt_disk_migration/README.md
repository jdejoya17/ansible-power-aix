# Ansible Role: alt_disk_migration
The [IBM Power Systems AIX](../../README.md) collection provides an [Ansible role](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html), referred to as `alt_disk_migration`, which automatically loads and executes commands to install dependent software.

For guides and reference, see the [Docs Site](https://ibm.github.io/ansible-power-aix/roles.html).

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values:

        nim_client (required)

Specifies a NIM object name that is associated to the NIM client LPAR to be migrated.

        target_disk (required)

Specifies the physical volume where the alternate disk will be created in the NIM client LPAR.

        lpp_source (required)

Specifies a NIM object name associated to a LPP resource for the desired level of migration.
If the object is not specified, the role will create a spot based on the I(lpp_source).

        spot (optional)

Specifies a NIM object name associated to a SPOT resource associated to the specified 
I(lpp_source).

## Dependencies

None.

## Example Playbook

    - name: Perfrom an alternate disk migration using hdisk1. Let the role build the spot.
      hosts: aix
      gather_facts: no
      tasks:
         - include_role:
              name: nim_alt_disk_migration
           vars:
              nim_client: p9zpa-ansible-test1
              target_disk:
              disk_name: hdisk1
              lpp_source: lpp_2134A_730

## Example Playbook

    - name: Perform an alternate disk migration and let the role choose the disk.
      hosts: aix
      gather_facts: no
      tasks:
         - include_role:
              name: nim_alt_disk_migration
           vars:
              nim_client: p9zpa-ansible-test1
              target_disk:
                 disk_size_policy: minimize
              lpp_source: lpp_2134A_730
              spot: spot_2134A_730

## Example Playbook

    # Useful when migrating multiple nodes concurrently. Use first the role to perform the
    # validation of the resources only once. Then you can migrate the nodes without doing verifications.

    - name: Validate the nim lpp and spot resources and exit the playbook.
      hosts: aix
      gather_facts: no
      tasks:
         - include_role:
              name: nim_alt_disk_migration
           vars:
              lpp_source: lpp_2134A_730
              spot: spot_2134A_730
              control_phases:
                 validate_nim_resources: true
                 perform_nim_migration: false

## Example Playbook

    # Useful when migrating multiple nodes concurrently. The role will prevent the validation of 
    # of the resoureces and just perform the migration. The role still will perform specific validations
    # for the nim client such as connectity, OS level and valid hardware platform for the OS.

    - name: Perform an alternate disk without the lpp or spot resources validation.
    - hosts: aix
      gather_facts: no
      tasks:
         - include_role:
              name: nim_alt_disk_migration
           vars:
              nim_client: p9zpa-ansible-test1
              target_disk:
                 disk_size_policy: minimize
              lpp_source: lpp_2134A_730
              spot: spot_2134A_730
              control_phases:
                 validate_nim_resources: false
                 perform_nim_migration: true

## Example Playbook

    # For debugging purposes: debug_skip_nimadm: true
    # Similar to modules "check_mode". Useful to execute all the validations and just exit before
    # performing the migration. 

    - name: Preview an alternate disk migration. Exit before running nimadm
    - hosts: aix
      gather_facts: no
      tasks:
         - include_role:
              name: nim_alt_disk_migration
           vars:
              nim_client: p9zpa-ansible-test1
              target_disk:
                 disk_size_policy: minimize
              lpp_source: lpp_2134A_730
              spot: spot_2134A_730
              control_phases:
                 validate_nim_resources: true
                 perform_nim_migration: true
              debug_skip_nimadm: true

## Copyright
© Copyright IBM Corporation 2022
