#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# ----------------------------------------------------------
#  Copyright (python) ,2016-2036, Sowell Tech. Co,Ltd
#  FileName: base.py
#  Author: vod_team
#  Email: info@sowell-tech.com
#  Version: 0.0.1
#  LastChange: 2016-12-12
#  History: modified by HeYong in December 12, 2016.
#  Desc:
# ----------------------------------------------------------
"""
import logging
import datetime
import traceback
from json import loads
from sqlalchemy import not_
from sqlalchemy import or_
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import func

from dao import SESSION


class BaseWrapper(object):
    """
        BaseWrapper类是对sqlalchemy中对数据库的基本操作的简单封装，包含基本的增删改查等方法。
    """

    session = SESSION()

    def __init__(self, model):
        self.model = model

    @staticmethod
    def to_dict(obj_dict):
        """转换为字典"""
        return dict((key, obj_dict[key]) for key in obj_dict
                    if not key.startswith("_") and key not in ["instance", "model", "session"])

    @staticmethod
    def to_filters(instance, argument_filters):

        """sql条件"""
        if not isinstance(argument_filters, list):
            argument_filters = loads(argument_filters)
        # Create Alchemy Filters
        alchemy_filters = []
        for argument_filter in argument_filters:
            # Resolve right attribute
            if "val" in argument_filter.keys():
                right = argument_filter["val"]
            elif "value" in argument_filter.keys():  # Because we hate abbr sometimes ...
                right = argument_filter["value"]
            else:
                right = None
            # Operator
            operator = argument_filter["op"]
            if operator in ["like"]:
                right = '%' + right + '%'
            # Resolve left attribute
            if "name" not in argument_filter:
                logging.warning("Missing field_name attribute 'name'")
            if argument_filter["name"] == "~":
                left = instance
                operator = "attr_is"
            else:
                left = getattr(instance, argument_filter["name"])
            # Operators from flask-restless
            if operator in ["is_null"]:
                alchemy_filters.append(left.is_(None))
            elif operator in ["is_not_null"]:
                alchemy_filters.append(left.isnot(None))
            elif operator in ["is"]:
                alchemy_filters.append(left.is_(right))
            elif operator in ["is_not"]:
                alchemy_filters.append(left.isnot(right))
            elif operator in ["==", "eq", "equals", "equals_to"]:
                alchemy_filters.append(left == right)
            elif operator in ["!=", "ne", "neq", "not_equal_to", "does_not_equal"]:
                alchemy_filters.append(left != right)
            elif operator in [">", "gt"]:
                alchemy_filters.append(left > right)
            elif operator in ["<", "lt"]:
                alchemy_filters.append(left < right)
            elif operator in [">=", "ge", "gte", "geq"]:
                alchemy_filters.append(left >= right)
            elif operator in ["<=", "le", "lte", "leq"]:
                alchemy_filters.append(left <= right)
            elif operator in ["ilike"]:
                alchemy_filters.append(left.ilike(right))
            elif operator in ["not_ilike"]:
                alchemy_filters.append(left.notilike(right))
            elif operator in ["like"]:
                alchemy_filters.append(left.like(right))
            elif operator in ["not_like"]:
                alchemy_filters.append(left.notlike(right))
            elif operator in ["match"]:
                alchemy_filters.append(left.match(right))
            elif operator in ["in"]:
                alchemy_filters.append(left.in_(right))
            elif operator in ["not_in"]:
                alchemy_filters.append(left.notin_(right))
            elif operator in ["has"] and isinstance(right, list):
                alchemy_filters.append(left.any(*right))
            elif operator in ["has"]:
                alchemy_filters.append(left.has(right))
            elif operator in ["any"]:
                alchemy_filters.append(left.any(right))
            # Additional Operators
            elif operator in ["between"]:
                alchemy_filters.append(left.between(*right))
            elif operator in ["contains"]:
                alchemy_filters.append(left.contains(right))
            elif operator in ["startswith"]:
                alchemy_filters.append(left.startswith(right))
            elif operator in ["endswith"]:
                alchemy_filters.append(left.endswith(right))
            # Additional Checks
            elif operator in ["attr_is"]:
                alchemy_filters.append(getattr(left, right))
            elif operator in ["method_is"]:
                alchemy_filters.append(getattr(left, right)())
            # Test comparator
            elif hasattr(left.comparator, operator):
                alchemy_filters.append(getattr(left.comparator, operator)(right))
            # Raise Exception
            else:
                logging.warning("Unknown operator")
        return alchemy_filters

    def _apply_kwargs(self, instance, **kwargs):
        """ """

        if 'filters' in kwargs:
            filters = kwargs.pop('filters')
            for alchemy_filter in self.to_filters(self.model, filters):
                instance = instance.filter(alchemy_filter)

        if 'not_' in kwargs or 'or_' in kwargs:
            operator = 'not_'
            if 'not_' in kwargs:
                argument_filters = kwargs.pop('not_')
            else:
                operator = "or_"
                argument_filters = kwargs.pop('or_')
            if not isinstance(argument_filters, list):
                argument_filters = loads(argument_filters)
            alchemy_list = None
            for filters in argument_filters:
                alchemy_list = []
                alchemy_list += self.to_filters(self.model, [filters])

            if operator == "not_":
                instance = instance.filter(not_(*alchemy_list))
            else:
                instance = instance.filter(or_(*alchemy_list))

        if 'order_by' in kwargs or 'direction' in kwargs:
            criterion_data = kwargs.pop('order_by')
            direction_data = kwargs.pop('direction')
            if isinstance(criterion_data, list):
                for index in xrange(0,len(criterion_data)):
                    criterion = criterion_data[index]
                    direction = direction_data[index]
                    if direction == 'asc':
                        expression = asc(getattr(self.model, criterion))
                    else:
                        expression = desc(getattr(self.model, criterion))
                    instance = instance.order_by(expression)
            else:
                if direction_data == 'asc':
                    expression = asc(getattr(self.model, criterion_data))
                else:
                    expression = desc(getattr(self.model, criterion_data))
                instance = instance.order_by(expression)

        if 'offset' in kwargs:
            offset = kwargs.pop('offset')
            f_offset = lambda instance: instance.offset(offset)
        else:
            f_offset = lambda instance: instance

        if 'limit' in kwargs:
            limit = kwargs.pop('limit')
            flimit = lambda instance: instance.limit(limit)
        else:
            flimit = lambda instance: instance

        instance = instance.filter_by(**kwargs)
        instance = f_offset(instance)
        instance = flimit(instance)
        return instance

    def insert(self, data):
        """插入"""
        result = {'errorcode': -1}
        session = SESSION()
        try:
            if data.has_key("create_time") is False and hasattr(self, "create_time"):
                setattr(self, "create_time", datetime.datetime.now())
                setattr(self, "update_time", datetime.datetime.now())
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            session.add(self)
            session.flush()
            result = self.to_dict(self.__dict__)
            session.commit()
            result["errorcode"] = 0

        except BaseException:
            session.rollback()
            logging.error(traceback.format_exc())
        finally:
            session.close()
            return result

    def get(self, *args):
        """
            query based on primary_keys
        """
        result = []
        session = SESSION()
        try:
            instance = session.query(self.model)
            if isinstance(args, tuple):
                for arg in args:
                    result.append(self.to_dict(instance.get(arg).__dict__))
            else:
                result.append(self.to_dict(instance.get(args).__dict__))

        except BaseException:
            logging.error(traceback.format_exc())
        session.close()
        return result

    def count(self, table_column, **kwargs):
        number = 0
        session = SESSION()
        try:
            instance = session.query(func.count(getattr(self.model, table_column)))
            number = self._apply_kwargs(instance, **kwargs).scalar()
        except:
            logging.error(traceback.format_exc())
        finally:
            session.close()
            return number

    def all(self, **kwargs):
        """查询所有"""

        result = []
        session = SESSION()
        try:
            instance = session.query(self.model)
            for row in self._apply_kwargs(instance, **kwargs).all():
                result.append(self.to_dict(row.__dict__))

        except BaseException:
            logging.error(traceback.format_exc())
        finally:
            print 2
            session.close()
            return result

    def all_ex(self, *args, **kwargs):
        """......"""

        result = []
        session = SESSION()
        try:
            ins = []
            if isinstance(args, tuple):
                for arg in args:
                    ins.append(getattr(self.model, arg))
            else:
                logging.error("allEx|type of args is not tuple!")
                return buffer
            instance = session.query(*ins)
            for item in self._apply_kwargs(instance, **kwargs).all():
                row = {}
                for key in item.keys():
                    row[key] = item.__getattribute__(key)
                result.append(row)

        except BaseException:
            logging.error(traceback.format_exc())
        session.close()
        return result

    def one(self, **kwargs):
        """查询一个值"""
        result = []
        session = SESSION()
        try:
            instance = session.query(self.model)
            result_class = self._apply_kwargs(instance, **kwargs).one()
            result.append(self.to_dict(result_class.__dict__))

        except BaseException:
            logging.error(traceback.format_exc())
        session.close()
        return result

    def delete(self, **kwargs):
        """删除"""
        session = SESSION()
        instance = session.query(self.model)
        print "instance::", instance
        print '**kwargs::::', kwargs
        number = 0
        try:
            number = self._apply_kwargs(instance, **kwargs).delete(synchronize_session=False)
            session.flush()
            session.commit()

        except BaseException:
            session.rollback()
            logging.error(traceback.format_exc())

        session.close()
        return number

    def update(self, values, **kwargs):
        """更新"""
        session = SESSION()
        instance = session.query(self.model)
        number = 0
        try:
            number = self._apply_kwargs(instance, **kwargs).update(values)
            for row in self._apply_kwargs(instance, **kwargs).all():
                if hasattr(row, 'update_time'):
                    setattr(row, 'update_time', datetime.datetime.now())
            session.flush()
            session.commit()

        except BaseException:
            session.rollback()
            logging.error(traceback.format_exc())
        session.close()
        return number

    def max(self, table_column, **kwargs):
        """最大值"""
        session = SESSION()
        instance = session.query(func.max(getattr(self.model, table_column)))
        session.close()
        return self._apply_kwargs(instance, **kwargs).scalar()

    def sum(self, table_column, **kwargs):
        number = 0
        session = SESSION()
        try:
            instance = session.query(func.sum(getattr(self.model, table_column)))
            number = self._apply_kwargs(instance, **kwargs).scalar()
        except BaseException:
            self.session.rollback()
            logging.error(traceback.format_exc())
        finally:
            session.close()
            return number

    def join_ex(self, join_data, argc, *args, **kwargs):
        """......"""
        result = []
        session = SESSION()
        try:
            ins = []
            if isinstance(args, tuple):
                for arg in args:
                    ins.append(getattr(self.model, arg))
            else:
                logging.error("join of args is not tuple!")
                return buffer
            if isinstance(argc, list):
                for darg in argc:
                    ins.append(getattr(join_data[0], darg))
            instance = session.query(*ins).join(join_data[0],join_data[1]==join_data[2])
            for item in self._apply_kwargs(instance, **kwargs).all():
                row = {}
                for key in item.keys():
                    row[key] = item.__getattribute__(key)
                result.append(row)

        except BaseException:
            logging.error(traceback.format_exc())
        session.close()
        return result
