import json
from abc import abstractproperty
from django.db import models
from django.db.models import Field, signals
from django.utils.translation import ugettext_lazy as _
from django.core import exceptions, validators
from django.dispatch import dispatcher
import datetime

'''
Convert. array of datetime.time(int, int, int) to string.
example
datetime.time(7, 8, 59) => '07:08:59'
'''
def loads(arr):
    for i in range (0, len(arr)):
        if isinstance(arr[i], list):
            loads(arr[i])
        else:
            arr[i] = str(arr[i])
    return arr

'''
Try to validate if returned array really consits of elements of required type
'''
def arrayvalidator(array):
    arr = array[0]
    elementtype = array[1]
    for i in range (0, len(arr)):
        if isinstance(arr[i], list):
            arrayvalidator([arr[i], elementtype])
        elif elementtype == type(datetime.time()):
            try:
                s = arr[i].split(':')
            except:
                raise exceptions.ValidationError(_(u"Wrong type of data inserted"))
            if len(s) > 3:#time should not be longer than 3 - hours, minutes, seconds, right?
                raise exceptions.ValidationError(_(u"Inserted time is not time"))
            for j in range (0, len(s)):
                try:
                    int(s[j])
                except:
                    raise exceptions.ValidationError(_(u"Inserted time is not time"))
                if len(s[j]) > 2:
                    raise exceptions.ValidationError(_(u"Inserted time is not time"))
        elif type(arr[i]) != elementtype:
            raise exceptions.ValidationError(_(u"Wrong type of data inserted"))

class ArrayFieldBase(models.Field):
    
    def __init__(self, *args, **kwargs):
        Field.__init__(self, validators = [arrayvalidator], **kwargs)
            
    def get_prep_value(self, value):
        if value == '':
            value = '{}'
        else:
            value = value.replace('[','{').replace(']','}')
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return json.dumps(value)

    def to_python(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        return value

    def south_field_triple(self):
        from south.modelsinspector import introspector
        name = '%s.%s' % (self.__class__.__module__ , self.__class__.__name__)
        args, kwargs = introspector(self)
        return name, args, kwargs

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value


class CharArrayField(ArrayFieldBase):
    """
    A character varying array field for PostgreSQL
    """
    description = _('Character varying array')

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors from to_python
        and validate are propagated. The correct value is returned if no error is
        raised.
        """
        value = self.to_python(value)
        self.validate(value, model_instance)
        try:
            v = eval(value)
        except:
            raise exceptions.ValidationError(_(u"Wrong type of data inserted"))
        for i in range(0, len(v)):
            self.run_validators([v[i], type(str())])
        value = str(v)
        return value

    def db_type(self, connection):
        if self.max_length is not None:
            return 'character varying(%s)[]' % self.max_length
        return 'character varying[]'

class TextArrayField(ArrayFieldBase):
    """
    A text array field for PostgreSQL
    """
    description = _('Text array')

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors from to_python
        and validate are propagated. The correct value is returned if no error is
        raised.
        """
        value = self.to_python(value)
        self.validate(value, model_instance)
        try:
            v = eval(value)
        except:
            raise exceptions.ValidationError(_(u"Wrong type of data inserted"))
        for i in range(0, len(v)):
            self.run_validators([v[i], type(str())])
        value = str(v)
        return value

    def db_type(self, connection):
        return 'text[]'

class IntegerArrayField(ArrayFieldBase):
    """
    An integer array field for PostgreSQL
    """
    description = _('Integer array')

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors from to_python
        and validate are propagated. The correct value is returned if no error is
        raised.
        """
        value = self.to_python(value)
        self.validate(value, model_instance)
        try:
            v = eval(value)
        except:
            raise exceptions.ValidationError(_(u"Wrong type of data inserted"))
        for i in range(0, len(v)):
            self.run_validators([v[i], type(int())])
        value = str(v)
        return value

    def db_type(self, connection):
        return 'integer[]'

class TimeArrayField(ArrayFieldBase):
    """
    A text array field for PostgreSQL
    """
    description = _('Time array')
    
    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors from to_python
        and validate are propagated. The correct value is returned if no error is
        raised.
        """
        value = self.to_python(value)
        self.validate(value, model_instance)
        try:
            v = eval(value)
        except:
            raise exceptions.ValidationError(_(u"Wrong type of data inserted"))
        for i in range(0, len(v)):
            self.run_validators([v[i], type(datetime.time())])
        value = str(v)
        return value

    def to_python(self, value):
        if not isinstance(value, basestring):
            value = str(value)
        return value
    
    def db_type(self, connection):
        return 'time[]'

    def contribute_to_class(self, cls, name):
        super(TimeArrayField, self).contribute_to_class(cls, name)
        signals.post_init.connect(self.post_init, cls, True)
 
    def post_init(self, **kwargs):
        instance = kwargs['instance']
        value = self.value_from_object(instance)
        if value:
            setattr(instance, self.attname, str(loads(value)))
        else:
            setattr(instance, self.attname, None)