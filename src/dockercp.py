#!/usr/bin/env python3

import argparse
import os
from io import BytesIO
import docker
import tarfile

DEFAULT_BUFFER_LENGTH = 4


class DockerCopy(object):
    def __dprint(self, msg=None):
        if msg and self.args.debug:
            print("DEBUG: ", msg)

    def __validate_path(self):
        self.__dprint("Validating paths...")
        # validating src path (if : on path using container path)
        res = {"ret_src": True,
               "ret_dest": True}

        if ':' in self.args.src:
            res['ret_src'] = True  # TODO: need to verify is the path is valid on container
        else:
            if not os.path.exists(self.args.src):
                print("Error: Source file doesn't exist. Aborting...")
                res['ret_src'] = False

        # validating dest path (if : on path using container path)
        if ':' in self.args.dest:
            res['ret_dest'] = True  # TODO: need to verify is the path is valid on container
        else:
            if os.path.isfile(self.args.dest):
                print("Error: Destination file already exist. Aborting...")
                res['ret_dest'] = False

        self.__dprint("Validating paths... OK")
        return res['ret_src'] and res['ret_dest']

    def __init__(self):
        """Initialize DockerCopy object, getting and validate aruments"""

        parser = argparse.ArgumentParser(description=("Copy files from/to Docker containers"))
        parser.add_argument("-d", "--debug", dest="debug", type=bool, default=False, help="Enable debug info")
        parser.add_argument("-b", "--buffer-length", dest="buffer_length", type=int, default=DEFAULT_BUFFER_LENGTH,
                            help="Specify the buffer length (bytes)")
        parser.add_argument("src", type=str, help=("Source."))
        parser.add_argument("dest", type=str, help=("Destination."))
        self.args = parser.parse_args()

        if not self.__validate_path():
            print("Something is wrong on your paths...")
            exit(1)

        self.client = docker.from_env()

    def copy(self):
        if ':' in self.args.src:
            # copy FROM container - [CONTAINER:]<path> <path>
            container_name = self.args.src.split(':')[0]
            s_path = self.args.src.split(':')[1]
            file_obj = BytesIO()
            self.__dprint("Getting file...")
            container = self.client.containers.get(container_name)

            try:
                stream, stat = container.get_archive(s_path)
                while stat['linkTarget']:  # need that because we need to follow synlink..
                    self.__dprint("    synlink found, get real file....")
                    s_path = stat['linkTarget']
                    stream, stat = container.get_archive(s_path)

                for i in stream:
                    file_obj.write(i)
                file_obj.seek(0)

                with tarfile.TarFile(mode="r", fileobj=file_obj) as pw_tar:
                    pw_tar.extractall(path=self.args.dest)

                return True
            except Exception as e:  # todo: need to catch right exception (eg: not found)
                print(str(e))
                return False

        else:
            # copy TO container - path [CONTAINER:]<path>
            container_name = self.args.dest.split(':')[0]
            dest_path = self.args.dest.split(':')[1]
            file_obj = BytesIO()
            self.__dprint("Sending file...")
            container = self.client.containers.get(container_name)

            pw_tar = tarfile.TarFile(fileobj=file_obj, mode='w')

            tarinfo = tarfile.TarInfo(name='test.file')

            pw_tar.addfile(tarinfo, file_obj)
            pw_tar.close()

            file_obj.seek(0)

            return container.put_archive(path=os.path.dirname(os.path.abspath(dest_path)), data=file_obj)



if __name__ == "__main__":
    dockercp = DockerCopy()
    if dockercp.copy():
        print("Success Copy!")
    else:
        print("Error on Copy")
