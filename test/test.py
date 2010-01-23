#! /usr/bin/env python

import os, sys
# set import path to app root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import protobuf_json

from pprint import pprint



import test_pb2 as pb_test

# create and fill test message
pb=pb_test.TestMessage()
pb.id=123
pb.b=b"\x08\xc8\x03\x12"
pb.query="some text"
pb.flag=True
pb.test_enum=2
msg=pb.nested_msg
msg.id=1010
msg.title="test title"
msg.url="http://example.com/"

msgs=pb.nested_msgs.add()
msgs.id=456
msgs.title="test title"
msgs.url="http://localhost/"

pb.rep_int.append(1)
pb.rep_int.append(2)

pb.bs.append("\x00\x01\x02\x03\x04");
pb.bs.append("\x05\x06\x07\x08\x09");

pb.Extensions[pb_test.query]='test ext'
pb.Extensions[pb_test.long]=53267

# convert it to JSON and back
pprint(pb.SerializeToString())
json_str=protobuf_json.pb2json(pb)
print json_str
pb2=protobuf_json.json2pb(pb_test.TestMessage, json_str)
pprint(pb2.SerializeToString())

if pb == pb2:
	print "Test passed."
else:
	print "Test FAILED!"
