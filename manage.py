from __future__ import annotations
import argparse
import shutil
from typing import Type, TypeVar, Literal
from enum import Enum
from abc import ABC
from pathlib import Path
import subprocess
import sys
import functools

printerr = functools.partial(print, file=sys.stderr)

DEFAULT_MINECRAFT_VERSION = '1.20.1'
DEFAULT_DOCKER = shutil.which('docker') or shutil.which('podman') or 'docker'

_T = TypeVar('_T')


class Action(Enum):
    SHOW_CONFIG = 'show-config'
    SYSTEMD_CHECK_INSTALLED = 'systemd-check-installed'
    SYSTEMD_INSTALL = 'systemd-install'
    BUILD_IMAGE = 'build-image'
    CREATE_CONTAINER = 'create-container'
    START_CONTAINER = 'start'
    STOP_CONTAINER = 'stop'
    CLEAR_CONTAINER = 'clear'
    BACKUP = 'backup'


class _CommandBase(ABC):
    def __init__(self, source: _CommandBase | None = None):
        if source:
            self.__dict__.update(vars(source))

    def cast(self, typ: Type[_T]) -> _T:
        if not issubclass(typ, _CommandBase):
            raise TypeError(typ)
        return typ(self)

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        pass

    def run(self) -> int:
        raise NotImplementedError()


class _SystemdArgsMixin(_CommandBase):
    systemd_unit = 'my-minecraft'
    systemd_backup_unit = 'my-minecraft-backup'
    systemd_mode: Literal['system', 'user'] = 'user'
    systemd_instance: str = 'default'

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        super().init_parser(parser)

        parser.add_argument('-m', '--mode', dest="systemd_mode",
                            choices=['system', 'user'], default=cls.systemd_mode,
                            help='whether to use systemd for a user, or for the whole system')
        parser.add_argument('-i', '--instance', dest="systemd_instance", metavar="NAME", default=cls.systemd_instance,
                            help="name of the systemd unit instance to work with; "
                            "e.g. 'default' means my-minecraft@default.service")

    @property
    def systemd_dir(self):
        if self.systemd_mode == 'system':
            return Path('/etc/systemd/system')
        return Path.home() / '.config/systemd/user'

    @property
    def systemd_service_file(self):
        return self.systemd_dir / f'{self.systemd_unit}@.service'

    @property
    def systemd_backup_file(self):
        return self.systemd_dir / f'{self.systemd_backup_unit}@.service'

    @property
    def systemd_backup_timer_file(self):
        return self.systemd_dir / f'{self.systemd_backup_unit}@.timer'


class _MinecraftVersionMixin(_CommandBase):
    minecraft_version: str = DEFAULT_MINECRAFT_VERSION

    @classmethod
    def init_parser(cls, parser: argparse.ArgumentParser):
        super().init_parser(parser)
        parser.add_argument('--minecraft-version', dest="minecraft_version",
                            default=DEFAULT_MINECRAFT_VERSION, help="which Minecraft version to build the server for")


class _DockerArgsMixin(_CommandBase):
    docker_exec: str = (shutil.which('docker')
                        or shutil.which('podman')
                        or 'docker')
    image_tag: str = 'noupload.local/my-minecraft'


class MainCommand(_CommandBase):
    action: str
    verbose: bool = False

    def subcommand(self):
        enum_val = Action(self.action)

        if enum_val == SystemdCheckInstalled.action:
            return SystemdCheckInstalled(self)

        raise ValueError("unknown subcommand", self.subcommand)

    def run(self) -> int:
        return self.subcommand().run()

    @classmethod
    def create_parser(cls, prog: str | None = None):
        parser = argparse.ArgumentParser(
            prog=prog, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('-v', '--verbose', dest='verbose',
                            action='store_true', default=False)
        subparsers = parser.add_subparsers(
            title='action', dest='action', required=True)

        subp = subparsers.add_parser(SystemdCheckInstalled.action.value,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     help='check if the server is installed to systemd')
        SystemdCheckInstalled.init_parser(subp)
        return parser


class SystemdCheckInstalled(MainCommand, _SystemdArgsMixin):
    action = Action.SYSTEMD_CHECK_INSTALLED

    def run(self):
        if not shutil.which('systemctl'):
            printerr('systemctl not found; is systemd even installed?')
            return 1

        try:
            subprocess.run(['systemd-analyze', 'verify', self.systemd_service_file],
                           check=True)
            subprocess.run(['systemd-analyze', 'verify', self.systemd_backup_file],
                           check=True)
            subprocess.run(['systemd-analyze', 'verify', self.systemd_backup_timer_file],
                           check=True)
        except subprocess.CalledProcessError as exc:
            printerr(exc)
            return 1

        print('OK')
        return 0


if __name__ == '__main__':
    raise SystemExit(MainCommand.create_parser(
    ).parse_args(namespace=MainCommand()).run())
