
'''
Convert Google's protobuf Messages into commented JavaScript code.
'''

# groups are deprecated and not supported;
# Note that preservation of unknown fields is currently not available for Python (c) google docs
# TODO: Support extensions

__version__='0.0.1'
__author__='Paul Dovbush <dpp@dpp.su>'


from google.protobuf.descriptor import FieldDescriptor as _FieldDescriptor
from google.protobuf.reflection import GeneratedProtocolMessageType as _GeneratedProtocolMessageType

def _jsWriter_type_bytes():
	return '""'
_jsWriter_type_bytes.__name__='bytes'

def _jsWriter_type_unicode():
	return '""'
_jsWriter_type_unicode.__name__='unicode'

def _jsWriter_type_bool():
	return 'false'
_jsWriter_type_bool.__name__='bool'

_jsWriter_types = {
	_FieldDescriptor.TYPE_DOUBLE: float,
	_FieldDescriptor.TYPE_FLOAT: float,
	_FieldDescriptor.TYPE_INT64: long,
	_FieldDescriptor.TYPE_UINT64: long,
	_FieldDescriptor.TYPE_INT32: int,
	_FieldDescriptor.TYPE_FIXED64: float,
	_FieldDescriptor.TYPE_FIXED32: float,
	_FieldDescriptor.TYPE_BOOL: _jsWriter_type_bool,
	_FieldDescriptor.TYPE_STRING: _jsWriter_type_unicode,
	# _FieldDescriptor.TYPE_MESSAGE: _msg2json,
	_FieldDescriptor.TYPE_BYTES: _jsWriter_type_bytes,
	_FieldDescriptor.TYPE_UINT32: int,
	_FieldDescriptor.TYPE_ENUM: int,
	_FieldDescriptor.TYPE_SFIXED32: float,
	_FieldDescriptor.TYPE_SFIXED64: float,
	_FieldDescriptor.TYPE_SINT32: int,
	_FieldDescriptor.TYPE_SINT64: long,
}

from StringIO import StringIO

class jsWriter(StringIO):
	_level = 0
	def begin_msg(self, name):
		self.write('/* %s */ {\n' % name)
		self._level+=1
	def end_msg(self):
		self._level-=1
		self.seek(self.pos-2)
		self.write(self.print_indent+'\n}')
	@property
	def print_indent(self):
		s=''
		for i in range(0, self._level):
			s+='\t'
		return s
	def _indent_value(self, value):
		if type(value) in (str, unicode,):
			value=value.replace('\n','\n'+self.print_indent)
			return value.rstrip()
		return value
	def print_field(self, field_type, name, value, repeated):

		self.write(self.print_indent+name+':')
		if repeated:
			if field_type:
				self.write('/* %s[] */'%field_type)
			self._level+=1
			self.write(('[\n'+self.print_indent+'%s\n')%self._indent_value(value))
			self._level-=1
			self.write(self.print_indent+']')
		else:
			if field_type:
				self.write('/* %s */'%field_type)
			self.write('%s'%self._indent_value(value))

		self.write(',\n')

def _msg2json(pb_msg):
	jso = jsWriter()
	try:
		fields = list(pb_msg.fields)
		# fields.extend(pb_msg.DESCRIPTOR.Extensions._known_extensions.values())
		jso.begin_msg(pb_msg.name)
		for field in fields:
			if field.is_extension:
				name = field.name+':ext'
			else:
				name = field.name
			if field.type == _FieldDescriptor.TYPE_MESSAGE:
				# ftype=field.message_type.name
				ftype=None
				value = _msg2json(field.message_type)
			else:
				ftype=_jsWriter_types[field.type].__name__
				value = _jsWriter_types[field.type]()
			jso.print_field(ftype, name, value, field.label == _FieldDescriptor.LABEL_REPEATED)
		jso.end_msg()
	except Exception, e:
		jso.seek(0)
		# e.args = (jso.read(),)
		print jso.read()
		raise
	jso.seek(0)
	return jso.read()

def proto2json(module):
	res = ''
	for pb_msg_name in dir(module):
		pb_msg = getattr(module, pb_msg_name)
		if not isinstance(pb_msg, _GeneratedProtocolMessageType):
			continue
		res += _msg2json(pb_msg.DESCRIPTOR) + '\n\n'
	return res

if __name__ == '__main__':
	from test import test_writer
