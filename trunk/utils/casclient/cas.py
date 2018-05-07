#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# ----------------------------------------------------------
#  Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
#  FileName: cas.py
#  Author: youshaoping
#  Email: youshaoping@sowell-tech.com
#  Version: cas 0.0.1
#  LastChange: 2016.08.06
#  Desc:
# ----------------------------------------------------------
"""
import ctypes
from ctypes import *

from utils import CAS_LIB_PATH

lib = cdll.LoadLibrary(CAS_LIB_PATH)


class casClient(object):
    def __init__(self, cas_log_path, cas_config_path):
        self.obj = lib.casClient_new(cas_log_path, cas_config_path)

    def authentication(self, s_token, s_username, s_uri, s_operation):
        if None not in (s_token, s_username, s_uri, s_operation):
            result = lib.casClient_authentication(self.obj, s_token, s_username, s_uri, s_operation)
            result = ctypes.string_at(result, -1)
            return result
        else:
            return "{'result':'Invalid argument'}"
