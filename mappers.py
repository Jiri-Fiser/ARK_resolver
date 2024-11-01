import os
from abc import ABC, abstractmethod
from enum import Enum
from json import load
from pathlib import Path
from typing import Callable, Union
from ark import ArkIdentifier


class ResolveError(LookupError):
    pass


class MapperWarning(Exception):
    pass


class MetadataFormat(Enum):
    Rdf_Json = 0
    Erc_Anvl = 1


class IdMapper(ABC):
    mappers: list['IdMapper'] = []

    @abstractmethod
    def get_url(self, ark: ArkIdentifier) -> str:
        pass

    @abstractmethod
    def get_metadata(self: str, ark: ArkIdentifier, fmt: MetadataFormat) -> str:
        pass

    @abstractmethod
    def is_responsible(self, ark: ArkIdentifier) -> bool:
        pass

    @staticmethod
    def get_mapper_for_ark(ark: ArkIdentifier) -> 'IdMapper':
        for mapper in IdMapper.mappers:
            if mapper.is_responsible(ark):
                return mapper
        raise ResolveError(f"Unsupported shoulder {ark.shoulder} of ARK {ark}")

    @staticmethod
    def loader(actions: list[Callable[[], 'IdMapper']], logger):
        for action in actions:
            try:
                mapper = action()
                IdMapper.mappers.append(mapper)
            except MapperWarning as e:
                logger.error(f"{str(e)}")


class JSONFileMapper(IdMapper):
    def __init__(self, dir_path: Union[Path, str], naan: str, shoulder: str):
        self.shoulder = shoulder
        self.naan = naan
        self._file_path = Path(dir_path) / (self.shoulder + ".json")
        if (not self._file_path.exists()
                or not self._file_path.is_file()
                or not os.access(self._file_path, os.R_OK)):
            raise MapperWarning(f"Non accessible JSON file {self._file_path.absolute()}")

    def load_map(self) -> dict:
        try:
            with open(self._file_path, "rt") as f:
                dmap = load(f)
        except Exception:
            raise RuntimeError(f"JSON file `{self._file_path} is not accessible`")
        return dmap

    def get_url(self, ark: ArkIdentifier) -> str:
        assert ark.naan == self.naan, f"Invalid NAAN in `{ark}` (supported {self.naan})"
        dmap = self.load_map()
        if ark.locid not in dmap:
            raise ResolveError(f"Unregistered ARK identifier `{ark}`")
        return dmap[ark.locid]["url"]

    def get_metadata(self: str, ark: ArkIdentifier, fmt: MetadataFormat) -> str:
        assert ark.naan == self.naan, f"Invalid NAAN in `{ark}` (supported {self.naan})"
        dmap = self.load_map()
        if ark.locid not in dmap:
            raise ResolveError(f"Unregistered ARK identifier `{ark}`")

        metadata = dmap[ark.locid]["meta"]
        metadata["@id"] = str(ark)
        if fmt == MetadataFormat.Rdf_Json:
            return metadata

    def is_responsible(self, ark: ArkIdentifier):
        return ark.naan == self.naan and ark.shoulder == self.shoulder


if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)
    naan = "77298"
    IdMapper.loader([
        lambda: JSONFileMapper("", naan, "example0"),
        ], logger)
    ark = ArkIdentifier.parse("ark:/77298/example0testa/?")
    mapper = IdMapper.get_mapper_for_ark(ark)
    print(mapper.get_url(ark))
    print(mapper.get_metadata(ark, MetadataFormat.Rdf_Json))



