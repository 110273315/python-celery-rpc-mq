# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sr_reward.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='sr_reward.proto',
  package='sr.reward',
  serialized_pb=_b('\n\x0fsr_reward.proto\x12\tsr.reward\"@\n\x06Header\x12\x0e\n\x06sender\x18\x01 \x02(\t\x12\x13\n\x0bsender_type\x18\x02 \x02(\t\x12\x11\n\tinvoke_id\x18\x03 \x01(\r\"^\n\x07Message\x12!\n\x06header\x18\x01 \x02(\x0b\x32\x11.sr.reward.Header\x12%\n\x07req_tag\x18\x06 \x01(\x0b\x32\x12.sr.reward.TagInfoH\x00\x42\t\n\x07\x63ontent\"*\n\x07TagInfo\x12\x0e\n\x06\x63ustid\x18\x01 \x02(\t\x12\x0f\n\x07tagtime\x18\x02 \x02(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_HEADER = _descriptor.Descriptor(
  name='Header',
  full_name='sr.reward.Header',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='sr.reward.Header.sender', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sender_type', full_name='sr.reward.Header.sender_type', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='invoke_id', full_name='sr.reward.Header.invoke_id', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=94,
)


_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='sr.reward.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='sr.reward.Message.header', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='req_tag', full_name='sr.reward.Message.req_tag', index=1,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='content', full_name='sr.reward.Message.content',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=96,
  serialized_end=190,
)


_TAGINFO = _descriptor.Descriptor(
  name='TagInfo',
  full_name='sr.reward.TagInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='custid', full_name='sr.reward.TagInfo.custid', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tagtime', full_name='sr.reward.TagInfo.tagtime', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=192,
  serialized_end=234,
)

_MESSAGE.fields_by_name['header'].message_type = _HEADER
_MESSAGE.fields_by_name['req_tag'].message_type = _TAGINFO
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['req_tag'])
_MESSAGE.fields_by_name['req_tag'].containing_oneof = _MESSAGE.oneofs_by_name['content']
DESCRIPTOR.message_types_by_name['Header'] = _HEADER
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['TagInfo'] = _TAGINFO

Header = _reflection.GeneratedProtocolMessageType('Header', (_message.Message,), dict(
  DESCRIPTOR = _HEADER,
  __module__ = 'sr_reward_pb2'
  # @@protoc_insertion_point(class_scope:sr.reward.Header)
  ))
_sym_db.RegisterMessage(Header)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'sr_reward_pb2'
  # @@protoc_insertion_point(class_scope:sr.reward.Message)
  ))
_sym_db.RegisterMessage(Message)

TagInfo = _reflection.GeneratedProtocolMessageType('TagInfo', (_message.Message,), dict(
  DESCRIPTOR = _TAGINFO,
  __module__ = 'sr_reward_pb2'
  # @@protoc_insertion_point(class_scope:sr.reward.TagInfo)
  ))
_sym_db.RegisterMessage(TagInfo)


# @@protoc_insertion_point(module_scope)
