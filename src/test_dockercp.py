# -*- coding: utf-8 -*-

import pytest

from .dockercp import *


class TestDockerCP(object):
    """
    Run tests on dockercp class
    """

    def setup(self):
        pass

    def test_parse_args_with_debug(self):
        args = (['-d=1', 'test:/etc/fedora-release', '.'])
        dockercp = DockerCopy(args)

        assert dockercp.args.debug == True

    def test_parse_args_diff_buffer(self):
        args = (['--buffer-length=6', 'test:/etc/fedora-release', '.'])
        dockercp = DockerCopy(args)

        assert dockercp.args.buffer_length == 6

    def test_parse_args_without_required_args(self):
        args = (['--buffer-length=6'])
        with pytest.raises(SystemExit):
            dockercp = DockerCopy(args)

    def test_copy_from_container_real_file(self):
        args = (['--buffer-length=6', 'test:/etc/hosts', '.'])
        dockercp = DockerCopy(args)

        assert dockercp.args.buffer_length == 6
        assert dockercp.copy()

    def test_copy_from_container_synlink_file(
            self):  # /etc/fedora-release is symlink to ../usr/lib/fedora-release on docker
        args = (['--buffer-length=6', 'test:/etc/fedora-release', '.'])
        dockercp = DockerCopy(args)

        assert dockercp.args.buffer_length == 6
        assert dockercp.copy()

    def test_copy_to_container_file_not_exist(self):
        """
        raise system exit = 1 when the file doesn't exist
        """
        args = (['--buffer-length=6', './nofile.file', 'test:/etc/'])

        with pytest.raises(SystemExit):
            dockercp = DockerCopy(args)

    def test_copy_to_container_file(self):
        args = (['--buffer-length=6', './test.file', 'test:/etc/'])

        dockercp = DockerCopy(args)

        assert dockercp.copy()

    def test_copy_from_container_no_container(self):
        """
        raise exception when container is not found
        """
        args = (['--buffer-length=6', 'nocontainer:/etc/fedora-release', '.'])
        dockercp = DockerCopy(args)
        with pytest.raises(Exception):
            dockercp.copy()
