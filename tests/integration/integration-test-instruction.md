## How to run integration test on your own AIX LPAR victim

### I. Important Files
1. /usr/local/lib/python\<version\>/site-packages/ansible_test/_data/inventory
2. /usr/local/lib/python\<version\>/site-packages/ansible_test/_internal/ansible_util.py
3. /usr/local/lib/python\<version\>/site-packages/ansible_test/_internal/executor.py

if you are using a python venv (virtual environment then it should be in):
1. \<path to virtual environment\>/lib/python\<version\>/site-packages/ansible_test/_data/inventory
2. \<path to virtual environment\>/lib/python\<version\>/site-packages/ansible_test/_internal/ansible_util.py
3. \<path to virtual environment\>/lib/python\<version\>/site-packages/ansible_test/_internal/executor.py

### II. changes needed for ansible_test/_data/inventory
- add these lines in the file
- this inventory file is the reason we can run `ansible-test integration` on
our own AIX LPAR

```
[testhost]
ansible-test1 ansible_host=<ip addr> ansible_user=root ansible_pass=<victim password> ansible_python_interpreter="/usr/bin/pyton"
```

where:

ip addr - is the IP address of your victim machine

victim password - password to your victim machine

### III. changes needed for ansible_test/_internal/ansible_util.py
- in the file find `ANSIBLE_PYTHON_INTERPRETER`
- then add the location of the python interpreter of your AIX LPAR
- use the location of /usr/bin/python3

e.g.
```
...
 if isinstance(args, PosixIntegrationConfig):
        ansible.update(dict(
            ANSIBLE_PYTHON_INTERPRETER='/usr/bin/python3',  # force tests to set ansible_python_interpreter in inventory
        ))

 env.update(ansible)
...
```

### IV. changes needed for ansible_test/_internal/executor.py
- in this file find the `gather_facts=` for `hosts = 'testhost'`
- the host here corresponds to the inventory file
- changing this will disable the fetching `ansible_facts` automatically

e.g.
```
...
    else:
        hosts = 'testhost'
        gather_facts = False
...
```

### V. running integration tests
- after you've completed the above steps, you are now
ready to run the integration tests

- to list all available integration test buckets run,
```
ansible-test integration --list-targets
```
note: you can find these test buckets under `tests/integration/targets`

- IMPORTANT NOTE: running the command `ansible-test integration` will run
ALL the test buckets, PLEASE DO NOT DO THIS WHEN DEVELOPING YOUR OWN TEST
BUCKET as it takes a while to complete the integration test

- in order to run a specific test bucket,
```
ansible-test integration <target name>
```
where,
target name - is any one of the items listed with `--list-targets`
