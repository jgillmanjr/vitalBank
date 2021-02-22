from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from typing import Dict, Iterable, Optional, Type
import json


class VitalObject:
    """
    A base class for Vital Objects
    """
    EXTENSION: str = None
    DIR: str = None
    name: str = None
    original_path: Optional[Path] = None
    _data: dict = None

    @classmethod
    def from_file(cls, filepath: Path) -> VitalObject:
        """
        Create an LFO from a file
        :param filepath:
        :return:
        """
        with filepath.open('r') as f:
            return cls(data=json.load(f), filepath=filepath)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __init__(self, data: dict, filepath: Optional[Path], **kwargs):
        self._modified = False
        self._data = data
        self.original_path = filepath
        self.top_level_keys = list(self._data.keys())

        if 'name' in self.top_level_keys:
            self.name = self._data['name']
        elif filepath is not None:
            self.name = filepath.stem
        elif 'name' in kwargs:
            self.name = kwargs['name']
        else:
            raise Exception('Unable to define name for object.')

    def rename(self, new_name: str) -> None:
        """
        Rename the object

        :param new_name:
        :return:
        """
        if 'name' in self.top_level_keys:
            self._data['name'] = new_name
        self.name = new_name
        self._modified = True

    def return_data(self) -> dict:
        """
        Return the raw underlying data

        :return:
        """
        return self._data

    def is_modified(self) -> bool:
        """
        Return a boolean indicating if the object has been modified from original creation

        :return:
        """
        return self._modified


class Lfo(VitalObject):
    """
    A Vital LFO
    """
    EXTENSION = 'vitallfo'
    DIR = 'LFOs'


class Preset(VitalObject):
    """
    A Vital Preset
    """
    EXTENSION = 'vital'
    DIR = 'Presets'


class Skin(VitalObject):
    """
    A Vital Skin
    """
    EXTENSION = 'vitalskin'
    DIR = 'Skins'


class Wavetable(VitalObject):
    """
    A Vital Wavetable
    """
    EXTENSION = 'vitaltable'
    DIR = 'Wavetables'


class Bank:
    """
    Represents a bank comprised of various VitalObjects
    """
    EXTENSION = 'vitalbank'

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __init__(self, bank_name: str, vital_objects: Optional[Iterable[VitalObject]]):
        self.name = bank_name
        self.elements: Dict[Type[VitalObject], Dict[str, VitalObject]] = dict()

        if vital_objects is not None:
            for vobj in vital_objects:
                self.add_object(vobj)

    def add_object(self, vital_object: VitalObject) -> None:
        """
        Add a VitalObject to the Bank

        :param vital_object:
        :return:
        """
        if not isinstance(vital_object, VitalObject):
            raise Exception(f'{type(vital_object).__name__} is not recognized as VitalObject.')

        self.elements.setdefault(type(vital_object), dict())
        self.elements[type(vital_object)][vital_object.name] = vital_object

    def write_file(self, filedir: Path):
        """
        Write the bank file to disk

        :param filedir: The directory to write to
        :return:
        """
        filepath = filedir.joinpath(f'{self.name}.{Bank.EXTENSION}')

        bankfile = ZipFile(file=filepath, mode='w', compression=ZIP_DEFLATED, compresslevel=9)

        for ct, ctd in self.elements.items():
            zdir = f'{self.name}/{ct.DIR}'
            for i in ctd.values():
                zfile = f'{zdir}/{i.name}.{ct.EXTENSION}'
                bankfile.writestr(zinfo_or_arcname=zfile, data=json.dumps(i.return_data()))

        bankfile.close()
