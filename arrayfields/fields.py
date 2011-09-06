import json
from abc import abstractproperty
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ArrayFieldBase(models.Field):
    def get_prep_value(self, value):
        if value == '':
            value = '{}'
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return json.dumps(value)

    def to_python(self, value):
        if isinstance(value, basestring):
            value = json.loads(value)
        return value

    def south_field_triple(self):
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__ , self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs


class CharArrayField(ArrayFieldBase):
    """
    A character varying array field for PostgreSQL
    """
    description = _('Character varying array')

    def db_type(self, connection):
        if self.max_length is not None:
            return 'character varying(%s)[]' % self.max_length
        return 'character varying[]'

class TextArrayField(ArrayFieldBase):
    """
    A text array field for PostgreSQL
    """
    description = _('Text array')

    def db_type(self, connection):
        return 'text[]'

class IntegerArrayField(ArrayFieldBase):
    """
    An integer array field for PostgreSQL
    """
    description = _('Integer array')

    def db_type(self, connection):
        return 'integer[]'

class TimeArrayField(ArrayFieldBase):
    """
    A text array field for PostgreSQL
    """
    description = _('Time array')

    def db_type(self, connection):
        return 'time[]'

