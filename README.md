dockercp
====

Repository made as exercise to build a python function to copy file from a docker container without using docker cli commands.

To test:

- Need Python 3
- Install the requirements.txt
- Run:

`$ docker run -d --name test fedora:25 /usr/bin/sleep`

`$ python3 dockercp.py --bufer-length=4 test:/etc/fedora-release .` 

`$ cat ./fedora-release ` 