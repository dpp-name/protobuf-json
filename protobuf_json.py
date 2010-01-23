# JSON serialization support for Google's protobuf Messages
# Copyright (c) 2009, Paul Dovbush
# All rights reserved.
# http://code.google.com/p/protobuf-json/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of <ORGANIZATION> nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Provide serialization and de-serialization of Google's protobuf Messages into/from JSON format.
'''

# groups are deprecated and not supported;
# Note that preservation of unknown fields is currently not available for Python (c) google docs

__version__='0.0.4'
__author__='Paul Dovbush <dpp@dpp.su>'



import json	# py2.6+ TODO: add support for other JSON serialization modules

from google.protobuf.descriptor import FieldDescriptor as _FieldDescriptor

class ParseError(Exception): pass

def _cast_json2pb(field, value, pb):
	ftype = _TYPE_TO_DESERIALIZE_METHOD.get(field.type, None)
	if ftype is not None:
		return ftype(value)
	raise NotImplementedError(ftype, field.type)

def _get_repeated_json2pb(field, value, pb_value):
	ftype = _TYPE_TO_DESERIALIZE_METHOD.get(field.type, None)
	if ftype is not None:
		pb_value.append(ftype(value))
	else:
		_json2pb(pb_value.add(), value)

def _json2pb(pb, js):
	for field in pb.DESCRIPTOR.fields:
		try:
			if not js.has_key(field.name):
				continue
			value = js[field.name]
			if field.label == _FieldDescriptor.LABEL_REPEATED:
				pb_value = getattr(pb, field.name, None)
				for repeated_value in value:
					_get_repeated_json2pb(field, repeated_value, pb_value)
			else:
				if field.message_type is not None:
					_json2pb(getattr(pb, field.name, None), value)
				else:
					setattr(pb, field.name, _cast_json2pb(field, value, pb))
		except:
			raise ParseError(pb.__class__.__name__, field.name, js)
	for field in pb.Extensions._known_extensions.values():
		try:
			if not js.has_key(field.name+':ext'):
				continue
			value = js[field.name+':ext']
			if field.label == _FieldDescriptor.LABEL_REPEATED:
				pb_value = pb.Extensions[field]
				for repeated_value in value:
					_get_repeated_json2pb(field, repeated_value, pb_value)
			else:
				if field.message_type is not None:
					_json2pb(pb.Extensions[field], value)
				else:
					pb.Extensions[field] = _cast_json2pb(field, value, pb)
		except:
			raise ParseError(pb.__class__.__name__, field.name, js)
	return pb




def _cast_pb2json(field, value):
	ftype = _TYPE_TO_SERIALIZE_METHOD.get(field.type, None)
	if ftype is not None:
		return ftype(value)
	raise NotImplementedError(ftype, field.type)

def _get_repeated_pb2json(field, value):
	ftype = _TYPE_TO_SERIALIZE_METHOD.get(field.type, None)
	if ftype is not None:
		return ftype(value)
	else:
		return _pb2json(value)

def _pb2json(pb):
	js = {}
	# fields = pb.DESCRIPTOR.fields #all fields
	fields = pb.ListFields()	#only filled (including extensions)
	for field,value in fields:
		try:
			if field.label == _FieldDescriptor.LABEL_REPEATED:
				js_value = []
				for repeated_value in value:
					js_value.append(_get_repeated_pb2json(field, repeated_value))
			else:
				if field.message_type is not None:
					js_value = _pb2json(value)
				else:
					js_value = _cast_pb2json(field, value)
			if field.is_extension:
				js[field.name+':ext'] = js_value
			else:
				js[field.name] = js_value
		except:
			raise ParseError(pb.__class__.__name__, field.name, js)
	return js


_TYPE_TO_SERIALIZE_METHOD = {
	_FieldDescriptor.TYPE_DOUBLE: float,
	_FieldDescriptor.TYPE_FLOAT: float,
	_FieldDescriptor.TYPE_INT64: long,
	_FieldDescriptor.TYPE_UINT64: long,
	_FieldDescriptor.TYPE_INT32: int,
	_FieldDescriptor.TYPE_FIXED64: float,
	_FieldDescriptor.TYPE_FIXED32: float,
	_FieldDescriptor.TYPE_BOOL: bool,
	_FieldDescriptor.TYPE_STRING: unicode,
	_FieldDescriptor.TYPE_MESSAGE: _pb2json,
	_FieldDescriptor.TYPE_BYTES: lambda x: x.encode('string_escape'),
	_FieldDescriptor.TYPE_UINT32: int,
	_FieldDescriptor.TYPE_ENUM: int,
	_FieldDescriptor.TYPE_SFIXED32: float,
	_FieldDescriptor.TYPE_SFIXED64: float,
	_FieldDescriptor.TYPE_SINT32: int,
	_FieldDescriptor.TYPE_SINT64: long,
}

_TYPE_TO_DESERIALIZE_METHOD = {
	_FieldDescriptor.TYPE_DOUBLE: float,
	_FieldDescriptor.TYPE_FLOAT: float,
	_FieldDescriptor.TYPE_INT64: long,
	_FieldDescriptor.TYPE_UINT64: long,
	_FieldDescriptor.TYPE_INT32: int,
	_FieldDescriptor.TYPE_FIXED64: float,
	_FieldDescriptor.TYPE_FIXED32: float,
	_FieldDescriptor.TYPE_BOOL: bool,
	_FieldDescriptor.TYPE_STRING: unicode,
	# _FieldDescriptor.TYPE_MESSAGE: _json2pb,	#handled specially
	_FieldDescriptor.TYPE_BYTES: lambda x: x.decode('string_escape'),
	_FieldDescriptor.TYPE_UINT32: int,
	_FieldDescriptor.TYPE_ENUM: int,
	_FieldDescriptor.TYPE_SFIXED32: float,
	_FieldDescriptor.TYPE_SFIXED64: float,
	_FieldDescriptor.TYPE_SINT32: int,
	_FieldDescriptor.TYPE_SINT64: long,
}


def json2pb(pb_ctor, json_str):
	''' convert JSON string to google.protobuf.descriptor instance '''
	return _json2pb(pb_ctor(), json.loads(json_str))


def pb2json(pb):
	''' convert google.protobuf.descriptor instance to JSON string '''
	return json.dumps(_pb2json(pb))



if __name__ == '__main__':
	from test import test
