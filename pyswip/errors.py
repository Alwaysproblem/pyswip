# -*- coding: utf-8 -*-

# Copyright 2007 Yuce Tekol <yucetekol@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = "PrologError", "ExistenceError"

from .const import PL_ENGINE_INVAL, PL_ENGINE_INUSE


class PrologError(Exception):

    def __init__(self, msg="", context=None):
        self.msg = msg
        self.context = context

    def __str__(self):
        return self.msg


class ExistenceError(PrologError):

    def __init__(self, term_type, what):
        super().__init__("Does not exist: %s %s" % (term_type, what))
        self.term_type = term_type
        self.what = what


class EngineError(PrologError):

    ENGINE_INVALID = PL_ENGINE_INVAL
    ENGINE_IN_USE = PL_ENGINE_INUSE

    _STATUS_MSG_MAP = {
        ENGINE_INVALID: "invalid_engine",
        ENGINE_IN_USE: "engine_in_use",
    }

    def __init__(self, status: int):
        msg = self._STATUS_MSG_MAP.get(status, "unknown_status")
        super().__init__(msg)
        self.status = status