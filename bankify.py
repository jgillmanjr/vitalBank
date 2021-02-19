from __future__ import annotations
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple, Union
from zipfile import ZipFile, ZIP_DEFLATED
import json


class Lfo:
    """
    A Vital LFO
    """
    EXTENSION = 'vitallfo'
    DIR = 'LFOs'

    @classmethod
    def from_file(cls, filepath: Path) -> Lfo:
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

    def __init__(self, data: dict, filepath: Optional[Path]):
        self._data = data
        self.original_path = filepath
        self.name = self._data['name']

    def rename(self, new_name: str):
        """
        Rename

        :param new_name:
        :return:
        """
        self._data['name'] = new_name
        self.name = self._data['name']


class Preset:
    """
    A Vital Preset
    """
    EXTENSION = 'vital'
    DIR = 'Presets'

    @classmethod
    def from_file(cls, filepath: Path) -> Preset:
        """
        Create an Preset from a file
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
        self._data = data
        self.original_path = filepath

        if filepath is not None:  # Differs  because it appears the name comes from the file
            self.name = filepath.stem
        else:
            self.name = kwargs['name']

    def rename(self, new_name: str):
        """
        Rename

        :param new_name:
        :return:
        """
        self.name = new_name


class Wavetable:
    """
    A Vital Wavetable
    """
    EXTENSION = 'vitaltable'
    DIR = 'Wavetables'

    @classmethod
    def from_file(cls, filepath: Path) -> Wavetable:
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

    def __init__(self, data: dict, filepath: Optional[Path]):
        self._data = data
        self.original_path = filepath
        self.name = self._data['name']

    def rename(self, new_name: str):
        """
        Rename

        :param new_name:
        :return:
        """
        self._data['name'] = new_name
        self.name = self._data['name']


class Bank:
    """
    Represents a bank comprised of LFOs, Presets, and Wavetables
    """
    EXTENSION = 'vitalbank'

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __init__(self, bank_name: str, lfos: Optional[Iterable[Lfo]], presets: Optional[Iterable[Preset]],
                 wavetables: Optional[Iterable[Wavetable]]):
        self.name = bank_name
        self.elements = {
            Lfo: {lfo.name: lfo for lfo in lfos} if lfos is not None else list(),
            Preset: {preset.name: preset for preset in presets} if presets is not None else list(),
            Wavetable: {wavetable.name: wavetable for wavetable in wavetables} if wavetables is not None else list(),
        }

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
            for i in ctd:
                zfile = f'{zdir}/{i.name}.{ct.EXTENSION}'
                bankfile.writestr(zinfo_or_arcname=zfile, data=json.dumps(i._data))

        bankfile.close()


TYPE_DATA = {
    Lfo: ('LFOs', 'vitallfo'),
    Preset: ('Presets', 'vital'),
    Wavetable: ('Wavetables', 'vitaltable'),
}

CONFIG_FILE = Path('config.json')
with CONFIG_FILE.open('r') as config_file:
    CONFIG = json.load(config_file)
    BASE_DIR = Path(CONFIG['base_preset_dir'])
    BANK_DIR = BASE_DIR.joinpath(CONFIG['bank_dir'])
    USER_DIR = BASE_DIR.joinpath('User')
    BANK_DELIM = CONFIG['delimiter']


def is_bank_obj(delim: str, vobj: Union[Lfo, Preset, Wavetable]) -> Optional[Union[Lfo, Preset, Wavetable]]:
    """
    If an object name contains the delmiter and matches the pattern for belonging in a bank, return it. None otherwise.
    First delimiter must be at the beginning

    :param delim: The delimiter for a bank name
    :param vobj: The object
    :return:
    """
    name_components = str(vobj).split(sep=delim)

    if len(name_components) > 2:
        raise Exception(f'{type(vobj).__name__} {vobj.name} appears to have multiple instances of the delimiter.')
    if len(name_components) == 2:
        return vobj
    else:
        return None


def bank_comps(delim: str, vobj: Union[Lfo, Preset, Wavetable]) -> Tuple[str, str]:
    """
    Return the bank name and the name of the object with the bank bits stripped out.

    :param delim:
    :param vobj:
    :return:
    """

    name_components = str(vobj).split(sep=delim)
    if len(name_components) > 2:
        raise Exception(f'{type(vobj).__name__} {vobj.name} appears to have multiple instances of the delimiter.')
    if len(name_components) == 2:
        bank_name = name_components[0].strip()  # Clean out leading and trailing white space
        obj_name = name_components[1].strip()  # Same
        return bank_name, obj_name
    else:
        raise Exception('Vital Object Name does not appear to contain a bank component.')


def main():
    banks: Dict[str, Bank] = dict()

    for clstype, typedata in TYPE_DATA.items():
        subdir = USER_DIR.joinpath(typedata[0])
        for f in subdir.glob('*'):
            if not f.is_dir() and f.suffix == f'.{clstype.EXTENSION}':
                vobj = clstype.from_file(filepath=f)
                if is_bank_obj(delim=BANK_DELIM, vobj=vobj) is not None:
                    bank_name, obj_name = bank_comps(delim=BANK_DELIM, vobj=vobj)
                    banks.setdefault(bank_name, Bank(bank_name=bank_name, lfos=None, presets=None, wavetables=None))
                    vobj.rename(new_name=obj_name)  # Set the "clean" name
                    banks[bank_name].elements[clstype].append(vobj)

    for bank in banks.values():
        print(bank.name)
        for ct, ctd in bank.elements.items():
            print(f'\t{ct.__name__}')
            for i in ctd:
                print(f'\t\t{i}')

        print(f'Writing Bank {bank.name}')

        if not BANK_DIR.exists():
            BANK_DIR.mkdir()

        bank.write_file(filedir=Path(BANK_DIR))


if __name__ == '__main__':
    main()
