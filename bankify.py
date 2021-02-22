from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional, Tuple
from vital import Bank, VitalObject
import json


CONFIG_FILE = Path('config.json')
with CONFIG_FILE.open('r') as config_file:
    CONFIG = json.load(config_file)
    BASE_DIR = Path(CONFIG['base_preset_dir'])
    BANK_DIR = BASE_DIR.joinpath(CONFIG['bank_dir'])
    USER_DIR = BASE_DIR.joinpath('User')
    BANK_DELIM = CONFIG['delimiter']


def is_bank_obj(delim: str, vobj: VitalObject) -> Optional[VitalObject]:
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


def bank_comps(delim: str, vobj: VitalObject) -> Tuple[str, str]:
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

    for clstype in VitalObject.__subclasses__():
        subdir = USER_DIR.joinpath(clstype.DIR)
        for f in subdir.glob('*'):
            if not f.is_dir() and f.suffix == f'.{clstype.EXTENSION}':
                vobj = clstype.from_file(filepath=f)
                if is_bank_obj(delim=BANK_DELIM, vobj=vobj) is not None:
                    bank_name, obj_name = bank_comps(delim=BANK_DELIM, vobj=vobj)
                    banks.setdefault(bank_name, Bank(bank_name=bank_name, vital_objects=None))
                    vobj.rename(new_name=obj_name)  # Set the "clean" name
                    banks[bank_name].add_object(vital_object=vobj)

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
