# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cf.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='cf.proto',
  package='cf',
  serialized_pb=_b('\n\x08\x63\x66.proto\x12\x02\x63\x66\"@\n\x06Header\x12\x0e\n\x06sender\x18\x01 \x02(\t\x12\x13\n\x0bsender_type\x18\x02 \x02(\t\x12\x11\n\tinvoke_id\x18\x03 \x01(\r\"\xbd\x01\n\x07Message\x12\x1a\n\x06header\x18\x01 \x02(\x0b\x32\n.cf.Header\x12,\n\rreq_send_text\x18\n \x01(\x0b\x32\x13.cf.SendTextRequestH\x00\x12-\n\rres_send_text\x18\x0b \x01(\x0b\x32\x14.cf.SendTextResponseH\x00\x12.\n\x10recv_text_notify\x18\x0c \x01(\x0b\x32\x12.cf.RecvTextNotifyH\x00\x42\t\n\x07\x63ontent\"\xbe\x01\n\x17\x43ustomerSearchCondition\x12\n\n\x02id\x18\n \x01(\t\x12\x15\n\rcf_account_id\x18\x0b \x01(\t\x12\x16\n\x0ewechat_open_id\x18\x0c \x01(\t\x12\x17\n\x0fwechat_union_id\x18\r \x01(\t\x12\x0c\n\x04\x63ode\x18\x12 \x01(\t\x12\x0e\n\x06\x61li_id\x18\x0e \x01(\t\x12\x0e\n\x06mobile\x18\x0f \x01(\t\x12\x12\n\ndevice_mac\x18\x10 \x01(\t\x12\r\n\x05\x65mail\x18\x11 \x01(\t\"v\n\x0fSendTextRequest\x12\x12\n\naccount_id\x18\n \x02(\t\x12>\n\x19\x63ustomer_search_condition\x18\x0b \x03(\x0b\x32\x1b.cf.CustomerSearchCondition\x12\x0f\n\x07\x63ontent\x18\x0c \x02(\t\"C\n\x10SendTextResponse\x12\x0f\n\x07\x65rrcode\x18\x01 \x02(\x05\x12\x0e\n\x06\x65rrmsg\x18\x02 \x01(\t\x12\x0e\n\x06result\x18\n \x03(\x05\"\x88\x01\n\x0eRecvTextNotify\x12$\n\x0bsource_type\x18\n \x02(\x0e\x32\x0f.cf.ESourceType\x12\x12\n\naccount_id\x18\x0b \x02(\t\x12+\n\x06sender\x18\x0c \x02(\x0b\x32\x1b.cf.CustomerSearchCondition\x12\x0f\n\x07\x63ontent\x18\r \x02(\t*A\n\x0b\x45SourceType\x12\x07\n\x03SMS\x10\x01\x12\n\n\x06WECHAT\x10\x02\x12\x07\n\x03\x41LI\x10\x03\x12\t\n\x05\x45MAIL\x10\x04\x12\t\n\x05OTHER\x10\n*B\n\x0e\x45\x43ontentFormat\x12\x07\n\x03TXT\x10\x01\x12\x08\n\x04HTML\x10\x02\x12\x08\n\x04JSON\x10\x03\x12\x07\n\x03XML\x10\x04\x12\n\n\x06\x42\x41SE64\x10\x05')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_ESOURCETYPE = _descriptor.EnumDescriptor(
  name='ESourceType',
  full_name='cf.ESourceType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SMS', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WECHAT', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ALI', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='EMAIL', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OTHER', index=4, number=10,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=795,
  serialized_end=860,
)
_sym_db.RegisterEnumDescriptor(_ESOURCETYPE)

ESourceType = enum_type_wrapper.EnumTypeWrapper(_ESOURCETYPE)
_ECONTENTFORMAT = _descriptor.EnumDescriptor(
  name='EContentFormat',
  full_name='cf.EContentFormat',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TXT', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HTML', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='JSON', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='XML', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BASE64', index=4, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=862,
  serialized_end=928,
)
_sym_db.RegisterEnumDescriptor(_ECONTENTFORMAT)

EContentFormat = enum_type_wrapper.EnumTypeWrapper(_ECONTENTFORMAT)
SMS = 1
WECHAT = 2
ALI = 3
EMAIL = 4
OTHER = 10
TXT = 1
HTML = 2
JSON = 3
XML = 4
BASE64 = 5



_HEADER = _descriptor.Descriptor(
  name='Header',
  full_name='cf.Header',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='cf.Header.sender', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sender_type', full_name='cf.Header.sender_type', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='invoke_id', full_name='cf.Header.invoke_id', index=2,
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
  serialized_start=16,
  serialized_end=80,
)


_MESSAGE = _descriptor.Descriptor(
  name='Message',
  full_name='cf.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='cf.Message.header', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='req_send_text', full_name='cf.Message.req_send_text', index=1,
      number=10, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='res_send_text', full_name='cf.Message.res_send_text', index=2,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='recv_text_notify', full_name='cf.Message.recv_text_notify', index=3,
      number=12, type=11, cpp_type=10, label=1,
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
      name='content', full_name='cf.Message.content',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=83,
  serialized_end=272,
)


_CUSTOMERSEARCHCONDITION = _descriptor.Descriptor(
  name='CustomerSearchCondition',
  full_name='cf.CustomerSearchCondition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='cf.CustomerSearchCondition.id', index=0,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cf_account_id', full_name='cf.CustomerSearchCondition.cf_account_id', index=1,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wechat_open_id', full_name='cf.CustomerSearchCondition.wechat_open_id', index=2,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wechat_union_id', full_name='cf.CustomerSearchCondition.wechat_union_id', index=3,
      number=13, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='code', full_name='cf.CustomerSearchCondition.code', index=4,
      number=18, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ali_id', full_name='cf.CustomerSearchCondition.ali_id', index=5,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mobile', full_name='cf.CustomerSearchCondition.mobile', index=6,
      number=15, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='device_mac', full_name='cf.CustomerSearchCondition.device_mac', index=7,
      number=16, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='email', full_name='cf.CustomerSearchCondition.email', index=8,
      number=17, type=9, cpp_type=9, label=1,
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
  serialized_start=275,
  serialized_end=465,
)


_SENDTEXTREQUEST = _descriptor.Descriptor(
  name='SendTextRequest',
  full_name='cf.SendTextRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='account_id', full_name='cf.SendTextRequest.account_id', index=0,
      number=10, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='customer_search_condition', full_name='cf.SendTextRequest.customer_search_condition', index=1,
      number=11, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='cf.SendTextRequest.content', index=2,
      number=12, type=9, cpp_type=9, label=2,
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
  serialized_start=467,
  serialized_end=585,
)


_SENDTEXTRESPONSE = _descriptor.Descriptor(
  name='SendTextResponse',
  full_name='cf.SendTextResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='errcode', full_name='cf.SendTextResponse.errcode', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='errmsg', full_name='cf.SendTextResponse.errmsg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='result', full_name='cf.SendTextResponse.result', index=2,
      number=10, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=587,
  serialized_end=654,
)


_RECVTEXTNOTIFY = _descriptor.Descriptor(
  name='RecvTextNotify',
  full_name='cf.RecvTextNotify',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='source_type', full_name='cf.RecvTextNotify.source_type', index=0,
      number=10, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='account_id', full_name='cf.RecvTextNotify.account_id', index=1,
      number=11, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sender', full_name='cf.RecvTextNotify.sender', index=2,
      number=12, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='cf.RecvTextNotify.content', index=3,
      number=13, type=9, cpp_type=9, label=2,
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
  serialized_start=657,
  serialized_end=793,
)

_MESSAGE.fields_by_name['header'].message_type = _HEADER
_MESSAGE.fields_by_name['req_send_text'].message_type = _SENDTEXTREQUEST
_MESSAGE.fields_by_name['res_send_text'].message_type = _SENDTEXTRESPONSE
_MESSAGE.fields_by_name['recv_text_notify'].message_type = _RECVTEXTNOTIFY
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['req_send_text'])
_MESSAGE.fields_by_name['req_send_text'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['res_send_text'])
_MESSAGE.fields_by_name['res_send_text'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['recv_text_notify'])
_MESSAGE.fields_by_name['recv_text_notify'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_SENDTEXTREQUEST.fields_by_name['customer_search_condition'].message_type = _CUSTOMERSEARCHCONDITION
_RECVTEXTNOTIFY.fields_by_name['source_type'].enum_type = _ESOURCETYPE
_RECVTEXTNOTIFY.fields_by_name['sender'].message_type = _CUSTOMERSEARCHCONDITION
DESCRIPTOR.message_types_by_name['Header'] = _HEADER
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['CustomerSearchCondition'] = _CUSTOMERSEARCHCONDITION
DESCRIPTOR.message_types_by_name['SendTextRequest'] = _SENDTEXTREQUEST
DESCRIPTOR.message_types_by_name['SendTextResponse'] = _SENDTEXTRESPONSE
DESCRIPTOR.message_types_by_name['RecvTextNotify'] = _RECVTEXTNOTIFY
DESCRIPTOR.enum_types_by_name['ESourceType'] = _ESOURCETYPE
DESCRIPTOR.enum_types_by_name['EContentFormat'] = _ECONTENTFORMAT

Header = _reflection.GeneratedProtocolMessageType('Header', (_message.Message,), dict(
  DESCRIPTOR = _HEADER,
  __module__ = 'cf_pb2'
  # @@protoc_insertion_point(class_scope:cf.Header)
  ))
_sym_db.RegisterMessage(Header)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'cf_pb2'
  # @@protoc_insertion_point(class_scope:cf.Message)
  ))
_sym_db.RegisterMessage(Message)

CustomerSearchCondition = _reflection.GeneratedProtocolMessageType('CustomerSearchCondition', (_message.Message,), dict(
  DESCRIPTOR = _CUSTOMERSEARCHCONDITION,
  __module__ = 'cf_pb2'
  # @@protoc_insertion_point(class_scope:cf.CustomerSearchCondition)
  ))
_sym_db.RegisterMessage(CustomerSearchCondition)

SendTextRequest = _reflection.GeneratedProtocolMessageType('SendTextRequest', (_message.Message,), dict(
  DESCRIPTOR = _SENDTEXTREQUEST,
  __module__ = 'cf_pb2'
  # @@protoc_insertion_point(class_scope:cf.SendTextRequest)
  ))
_sym_db.RegisterMessage(SendTextRequest)

SendTextResponse = _reflection.GeneratedProtocolMessageType('SendTextResponse', (_message.Message,), dict(
  DESCRIPTOR = _SENDTEXTRESPONSE,
  __module__ = 'cf_pb2'
  # @@protoc_insertion_point(class_scope:cf.SendTextResponse)
  ))
_sym_db.RegisterMessage(SendTextResponse)

RecvTextNotify = _reflection.GeneratedProtocolMessageType('RecvTextNotify', (_message.Message,), dict(
  DESCRIPTOR = _RECVTEXTNOTIFY,
  __module__ = 'cf_pb2'
  # @@protoc_insertion_point(class_scope:cf.RecvTextNotify)
  ))
_sym_db.RegisterMessage(RecvTextNotify)


# @@protoc_insertion_point(module_scope)
