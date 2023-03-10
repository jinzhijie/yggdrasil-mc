import json
from base64 import b64decode
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, root_validator


class YggdrasilPlayerUuidApi(BaseModel):
    id: str | None = None
    name: str | None = None
    existed: bool = True


def _make_hash(cls, values):
    url: str = values["url"]
    last_slash_location = url.rindex("/")
    real_hash = url[last_slash_location + 1 :]
    values["hash"] = real_hash
    return values


class YggdrasilTextures(BaseModel):
    class _Skin(BaseModel):
        class MetaData(BaseModel):
            model: Literal["default", "slim"] = "default"

        url: str | None = None
        hash: str | None = None
        metadata: MetaData | None = MetaData(model="default")
        _hash: str | None = None

        root_validator(pre=True, allow_reuse=True)(_make_hash)

    class _Cape(BaseModel):
        url: str | None = None
        hash: str | None = None
        _hash: str | None = None

        root_validator(pre=True, allow_reuse=True)(_make_hash)

    skin: _Skin = Field(default_factory=_Skin, alias="SKIN")
    cape: _Cape = Field(default_factory=_Cape, alias="CAPE")


class YggdrasilPropertiesTextures(BaseModel):
    timestamp: date
    profileId: str
    profileName: str
    textures: YggdrasilTextures


class YggdrasilGameProfileApi(BaseModel):
    class Properties(BaseModel):
        textures: YggdrasilPropertiesTextures

    id: str
    name: str
    properties: Properties  # a bit difference between API

    @root_validator(pre=True)
    def pre_processer(cls, values):
        # Doc: https://wiki.vg/Mojang_API#UUID_-.3E_Profile_.2B_Skin.2FCape
        # base64 decode and a little change
        values["properties"][0]["textures"] = json.loads(
            b64decode(values["properties"][0]["value"])
        )
        # array is useless while mojang is interesting
        values["properties"] = values["properties"][0]
        return values
