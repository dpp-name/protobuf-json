#! /usr/bin/env python

import os, sys
# set import path to app root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import protobuf_json_writer

from pprint import pprint



import test_pb2 as pb_test

# print protobuf_json_writer._msg2json(pb_test.TestMessage.DESCRIPTOR)
print protobuf_json_writer.proto2json(pb_test)