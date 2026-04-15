import re
from dataclasses import dataclass
from urllib.parse import quote_plus

naan_pattern = "(?P<naan>[0-9]+)"
shoulder_pattern = "(?P<shoulder>[a-z-]+[0-9]+)?"

path_splitter = re.compile(
    r"""(ark|ARK):/?(?P<naan>[0-9]+) # NAAN fixed prefix
    /+
    (?P<shoulder>[a-z-]+[0-9]+)?  #shoulder (name space)
    (?P<locid>.*) #id in shoulder namespace
    """, flags=re.X)


class ArkFormatError(Exception):
    pass


@dataclass
class ArkIdentifier:
    naan: str
    shoulder: str
    locid: str

    def __str__(self):
        """
        User readable form of ARK identifier (primary use: displayed or printed test)
        :return:
        """
        return f"ark:/{self.naan}/{self.shoulder}{self.locid}"

    def __repr__(self):
        """
        Canonical form of ARK identifier (primary use: part of URLs)
        :return:
        """
        return  ArkIdentifier.normalize_id(f"ark:/{self.naan}/{self.shoulder}{self.locid}")

    @staticmethod
    def normalize_id(ident: str) -> str:
        def to_upper(match):
            return f"%{match.group(1).upper()}"
        ident = quote_plus(ident)
        ident = ident.replace("-", "")
        ident = ident.rstrip("/")
        ident = re.sub("([/.])[\1]+", r"\1", ident)
        ident = re.sub(r'%([0-9a-fA-F]{2})', to_upper, ident)
        return ident

    @staticmethod
    def create(naan: str, shoulder: str, locid: str) -> 'ArkIdentifier':
        return ArkIdentifier(naan, shoulder, ArkIdentifier.normalize_id(locid))

    @staticmethod
    def parse(ark_string: str) -> 'ArkIdentifier':
        match = path_splitter.match(ark_string)
        if not match:
            raise ArkFormatError(f"Identifier `{ark_string}` is not parsable ARK identifier")
        return ArkIdentifier.create(match.group("naan"), match.group("shoulder"),
                                    ArkIdentifier.normalize_id(match.group("locid")))


