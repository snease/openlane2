# Copyright 2023 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
from decimal import Decimal
from typing import Any, Tuple
from collections import UserDict, UserString

from .resolve import resolve


class Path(UserString):
    pass


class ConfigEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o.as_integer_ratio()[1] == 1:
                return int(o)
            else:
                return float(o)
        elif isinstance(o, Path):
            return str(o)
        return super(ConfigEncoder, self).default(o)


class DecimalDecoder(json.JSONDecoder):
    def default(self, o):
        if isinstance(o, float) or isinstance(o, int):
            return Decimal(o)
        return super(DecimalDecoder, self).default(o)


class Config(UserDict):
    @classmethod
    def from_json(Self, json_in: str, **kwargs) -> "Config":
        resolved = resolve(
            json.loads(json_in, cls=DecimalDecoder),
            **kwargs,
        )

        config = Self()  # TODO: Schema Validation
        config.update(resolved)
        return config

    def to_json(self) -> str:
        return json.dumps(self.data, indent=2, cls=ConfigEncoder, sort_keys=True)

    def check(self, key: str) -> Tuple[bool, Any]:
        return (key in self.keys(), self.get(key))

    def extract(self, key: str) -> Tuple[bool, Any]:
        found, value = self.check(key)
        if found:
            del self[key]
        return (found, value)
