#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# ----------------------------------------------------------
#  Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
#  FileName: config.py
#  Author: wangdean
#  Email: wangdean@sowell-tech.com
#  Version: config 0.0.1
#  LastChange: 2014.12.29
#  Desc:
#  History: modified by ZhongXin  in July 31, 2016.
# ----------------------------------------------------------
"""
import os
import logging
import ConfigParser


# Modified the get option value case-insensitive question.
class Parser(ConfigParser.ConfigParser):
    """Parser类"""
    def __init__(self, defaults=None):
        ConfigParser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class Config(object):
    """Config类"""
    def __init__(self):
        self.conf = Parser()
        self.mtime = None
        self.path = None

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            org = super(Config, cls)
            cls._instance = org.__new__(cls)
        return cls._instance

    def set_config(self, path):
        """设置配置文件"""
        if os.path.isfile(path):
            self.path = path
            self.mtime = os.path.getmtime(path)
            self.conf.read(path)
        else:
            logging.error('config file[%s] is not exist.', path)

    def reload(self):
        """重载配置文件"""
        self.mtime = os.path.getmtime(self.path)
        self.conf.read(self.path)

    def get_sections(self):
        """获取某个选项"""
        try:
            return self.conf.sections()
        except BaseException:
            logging.error('getSections error.')
            return []

    def get_items(self, section):
        """获取某一项的值"""
        try:
            return self.conf.items(section)
        except BaseException:
            logging.error('getItems[%s] error.', section)
            return []

    def get_options(self, section):
        """获取某一项的键"""
        try:
            return self.conf.options(section)
        except BaseException:
            logging.error('getOptions[%s]error.', section)
            return []

    def get(self, field, key, default='', field_type='str'):
        """类型转换"""
        try:
            if os.path.getmtime(self.path) != self.mtime:
                self.reload()
            if field_type == 'int':
                result = self.conf.getint(field, key)
            elif field_type == 'boolean':
                result = self.conf.getboolean(field, key)
            elif field_type == 'float':
                result = self.conf.getfloat(field, key)
            else:
                result = self.conf.get(field, key)
        except BaseException:
            logging.error('get field[%s] key[%s] failed.', field, key)
            result = default
        return result

    def add_section(self, section):
        """增加项"""
        self.conf.add_section(section)

    def set(self, field, key, value):
        """设置"""
        try:
            self.conf.set(field, key, value)
            self.conf.write(open(self.path, 'w'))
        except BaseException:
            logging.error('set field[%s] key[%s] value[%s] failed.', field, key, value)
            return False
        return True
