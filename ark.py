import re
from dataclasses import dataclass

path_splitter = re.compile(
    r"""(ark|ARK):/?(?P<naan>[0-9]+) # NAAN fixed prefix
    /+
    (?P<shoulder>[a-z-]+[0-9]+)?  #shoulder (name space)
    (?P<locid>[=%*+~@$A-Za-z0-9/._-]*) #id in namespace
    """, flags=re.X)


class ArkFormatError(Exception):
    pass
@dataclass
class ArkIdentifier:
    naan: str
    shoulder: str
    locid: str

    def __repr__(self):
        return f"ark:/{self.naan}/{self.shoulder}{self.locid}"

    @staticmethod
    def normalize_id(ident: str) -> str:
        def to_upper(match):
            return f"%{match.group(1).upper()}"
        ident = ident.replace("-", "")
        ident = ident.rstrip("/")
        ident = re.sub("([/.])[/.]+", r"\1", ident)
        ident = re.sub(r'%([0-9a-fA-F]{2})', to_upper, ident)
        return ident

    @staticmethod
    def parse(ark_string: str) -> 'ArkIdentifier':
        match = path_splitter.match(ark_string)
        if not match:
            raise ArkFormatError(f"Identifier `{ark_string}` is not parsable ARK identifier")
        return ArkIdentifier(ArkIdentifier.normalize_id(match.group("naan")),
                            ArkIdentifier.normalize_id(match.group("shoulder")),
                            ArkIdentifier.normalize_id(match.group("locid")))


