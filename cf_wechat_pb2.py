# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cf_wechat.proto

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
  name='cf_wechat.proto',
  package='cf.wechat',
  serialized_pb=_b('\n\x0f\x63\x66_wechat.proto\x12\tcf.wechat\"@\n\x06Header\x12\x0e\n\x06sender\x18\x01 \x02(\t\x12\x13\n\x0bsender_type\x18\x02 \x02(\t\x12\x11\n\tinvoke_id\x18\x03 \x01(\r\"\xb6\x03\n\x07Message\x12!\n\x06header\x18\x01 \x02(\x0b\x32\x11.cf.wechat.Header\x12\x44\n\x16req_group_message_send\x18\r \x01(\x0b\x32\".cf.wechat.GroupMessageSendRequestH\x00\x12\x45\n\x16res_group_message_send\x18\x0e \x01(\x0b\x32#.cf.wechat.GroupMessageSendResponseH\x00\x12\x38\n\x12req_userinfo_query\x18\x13 \x01(\x0b\x32\x1a.cf.wechat.UserInfoRequestH\x00\x12\x39\n\x12res_userinfo_query\x18\x14 \x01(\x0b\x32\x1b.cf.wechat.UserInfoResponseH\x00\x12<\n\x11req_userinfo_sync\x18\xdb\x01 \x01(\x0b\x32\x1e.cf.wechat.SyncUserInfoRequestH\x00\x12=\n\x11res_userinfo_sync\x18\xdc\x01 \x01(\x0b\x32\x1f.cf.wechat.SyncUserInfoResponseH\x00\x42\t\n\x07\x63ontent\"\xbe\x01\n\x17\x43ustomerSearchCondition\x12\n\n\x02id\x18\n \x01(\t\x12\x15\n\rcf_account_id\x18\x0b \x01(\t\x12\x16\n\x0ewechat_open_id\x18\x0c \x01(\t\x12\x17\n\x0fwechat_union_id\x18\r \x01(\t\x12\x0c\n\x04\x63ode\x18\x12 \x01(\t\x12\x0e\n\x06\x61li_id\x18\x0e \x01(\t\x12\x0e\n\x06mobile\x18\x0f \x01(\t\x12\x12\n\ndevice_mac\x18\x10 \x01(\t\x12\r\n\x05\x65mail\x18\x11 \x01(\t\"\x94\x01\n\x0fUserInfoRequest\x12\x12\n\naccount_id\x18\n \x02(\t\x12\x45\n\x19\x63ustomer_search_condition\x18\x0b \x03(\x0b\x32\".cf.wechat.CustomerSearchCondition\x12&\n\x08language\x18\x0c \x01(\x0e\x32\x14.cf.wechat.ELanguage\"\xab\x03\n\x10UserInfoResponse\x12\x0f\n\x07\x65rrcode\x18\x01 \x02(\x05\x12\x0e\n\x06\x65rrmsg\x18\x02 \x01(\t\x12\x34\n\x06result\x18\x03 \x03(\x0b\x32$.cf.wechat.UserInfoResponse.UserInfo\x1a\xbf\x02\n\x08UserInfo\x12\x11\n\twxerrcode\x18\n \x01(\x05\x12?\n\x08wxresult\x18\x0b \x01(\x0b\x32-.cf.wechat.UserInfoResponse.UserInfo.WxResult\x1a\xde\x01\n\x08WxResult\x12\x11\n\tsubscribe\x18\x14 \x01(\x08\x12\x0e\n\x06openid\x18\x15 \x02(\t\x12\x10\n\x08nickname\x18\x16 \x02(\t\x12\x0b\n\x03sex\x18\x17 \x02(\x05\x12\x0f\n\x07\x63ountry\x18\x19 \x02(\t\x12\x10\n\x08province\x18\x1a \x02(\t\x12\x0c\n\x04\x63ity\x18\x18 \x02(\t\x12\x13\n\x0b\x61vatar_uuid\x18\x1c \x02(\t\x12\x16\n\x0esubscribe_time\x18\x1d \x02(\x04\x12\x10\n\x08union_id\x18\x1e \x01(\t\x12\x0e\n\x06remark\x18\x1f \x02(\t\x12\x10\n\x08group_id\x18  \x01(\x05\"\x98\x01\n\x13SyncUserInfoRequest\x12\x12\n\naccount_id\x18\n \x02(\t\x12\x45\n\x19\x63ustomer_search_condition\x18\x0b \x01(\x0b\x32\".cf.wechat.CustomerSearchCondition\x12&\n\x08language\x18\x0c \x01(\x0e\x32\x14.cf.wechat.ELanguage\"a\n\x14SyncUserInfoResponse\x12\x0f\n\x07\x65rrcode\x18\x01 \x02(\x05\x12\x0e\n\x06\x65rrmsg\x18\x02 \x01(\t\x12\x13\n\x0bopenid_list\x18\x03 \x03(\t\x12\x13\n\x0bnext_openid\x18\x04 \x01(\t\"\xcd\x01\n\x17GroupMessageSendRequest\x12\x12\n\naccount_id\x18\n \x02(\t\x12\x45\n\x19\x63ustomer_search_condition\x18\r \x03(\x0b\x32\".cf.wechat.CustomerSearchCondition\x12\x10\n\x08group_id\x18\x14 \x01(\t\x12\x32\n\x0fmessage_content\x18\x0e \x03(\x0b\x32\x19.cf.wechat.MessageContent\x12\x11\n\tis_record\x18\x0f \x01(\x08\"K\n\x18GroupMessageSendResponse\x12\x0f\n\x07\x65rrcode\x18\x01 \x02(\x05\x12\x0e\n\x06\x65rrmsg\x18\x02 \x01(\t\x12\x0e\n\x06msg_id\x18\x03 \x01(\x05\"[\n\x0eMessageContent\x12#\n\x04type\x18\n \x02(\x0e\x32\x15.cf.wechat.EMediaType\x12\x13\n\x0bresource_id\x18\x14 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x1e \x01(\t*o\n\nEMediaType\x12\x08\n\x04NEWS\x10\x01\x12\x08\n\x04TEXT\x10\x02\x12\t\n\x05VOICE\x10\x03\x12\t\n\x05MUSIC\x10\x04\x12\t\n\x05IMAGE\x10\x05\x12\t\n\x05VIDEO\x10\x06\x12\t\n\x05THUMB\x10\x07\x12\n\n\x06WXCARD\x10\x08\x12\n\n\x06MPNEWS\x10\t*#\n\tELanguage\x12\x06\n\x02\x45N\x10\x01\x12\x06\n\x02\x43N\x10\x02\x12\x06\n\x02TW\x10\x03')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_EMEDIATYPE = _descriptor.EnumDescriptor(
  name='EMediaType',
  full_name='cf.wechat.EMediaType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NEWS', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TEXT', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VOICE', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MUSIC', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IMAGE', index=4, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='VIDEO', index=5, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='THUMB', index=6, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='WXCARD', index=7, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MPNEWS', index=8, number=9,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1943,
  serialized_end=2054,
)
_sym_db.RegisterEnumDescriptor(_EMEDIATYPE)

EMediaType = enum_type_wrapper.EnumTypeWrapper(_EMEDIATYPE)
_ELANGUAGE = _descriptor.EnumDescriptor(
  name='ELanguage',
  full_name='cf.wechat.ELanguage',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='EN', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CN', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TW', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=2056,
  serialized_end=2091,
)
_sym_db.RegisterEnumDescriptor(_ELANGUAGE)

ELanguage = enum_type_wrapper.EnumTypeWrapper(_ELANGUAGE)
NEWS = 1
TEXT = 2
VOICE = 3
MUSIC = 4
IMAGE = 5
VIDEO = 6
THUMB = 7
WXCARD = 8
MPNEWS = 9
EN = 1
CN = 2
TW = 3



_HEADER = _descriptor.Descriptor(
  name='Header',
  full_name='cf.wechat.Header',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='cf.wechat.Header.sender', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sender_type', full_name='cf.wechat.Header.sender_type', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='invoke_id', full_name='cf.wechat.Header.invoke_id', index=2,
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
  full_name='cf.wechat.Message',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='header', full_name='cf.wechat.Message.header', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='req_group_message_send', full_name='cf.wechat.Message.req_group_message_send', index=1,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='res_group_message_send', full_name='cf.wechat.Message.res_group_message_send', index=2,
      number=14, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='req_userinfo_query', full_name='cf.wechat.Message.req_userinfo_query', index=3,
      number=19, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='res_userinfo_query', full_name='cf.wechat.Message.res_userinfo_query', index=4,
      number=20, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='req_userinfo_sync', full_name='cf.wechat.Message.req_userinfo_sync', index=5,
      number=219, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='res_userinfo_sync', full_name='cf.wechat.Message.res_userinfo_sync', index=6,
      number=220, type=11, cpp_type=10, label=1,
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
      name='content', full_name='cf.wechat.Message.content',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=97,
  serialized_end=535,
)


_CUSTOMERSEARCHCONDITION = _descriptor.Descriptor(
  name='CustomerSearchCondition',
  full_name='cf.wechat.CustomerSearchCondition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='cf.wechat.CustomerSearchCondition.id', index=0,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cf_account_id', full_name='cf.wechat.CustomerSearchCondition.cf_account_id', index=1,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wechat_open_id', full_name='cf.wechat.CustomerSearchCondition.wechat_open_id', index=2,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wechat_union_id', full_name='cf.wechat.CustomerSearchCondition.wechat_union_id', index=3,
      number=13, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='code', full_name='cf.wechat.CustomerSearchCondition.code', index=4,
      number=18, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ali_id', full_name='cf.wechat.CustomerSearchCondition.ali_id', index=5,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mobile', full_name='cf.wechat.CustomerSearchCondition.mobile', index=6,
      number=15, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='device_mac', full_name='cf.wechat.CustomerSearchCondition.device_mac', index=7,
      number=16, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='email', full_name='cf.wechat.CustomerSearchCondition.email', index=8,
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
  serialized_start=538,
  serialized_end=728,
)


_USERINFOREQUEST = _descriptor.Descriptor(
  name='UserInfoRequest',
  full_name='cf.wechat.UserInfoRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='account_id', full_name='cf.wechat.UserInfoRequest.account_id', index=0,
      number=10, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='customer_search_condition', full_name='cf.wechat.UserInfoRequest.customer_search_condition', index=1,
      number=11, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='language', full_name='cf.wechat.UserInfoRequest.language', index=2,
      number=12, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
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
  serialized_start=731,
  serialized_end=879,
)


_USERINFORESPONSE_USERINFO_WXRESULT = _descriptor.Descriptor(
  name='WxResult',
  full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='subscribe', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.subscribe', index=0,
      number=20, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='openid', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.openid', index=1,
      number=21, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nickname', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.nickname', index=2,
      number=22, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sex', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.sex', index=3,
      number=23, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='country', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.country', index=4,
      number=25, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='province', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.province', index=5,
      number=26, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='city', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.city', index=6,
      number=24, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avatar_uuid', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.avatar_uuid', index=7,
      number=28, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='subscribe_time', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.subscribe_time', index=8,
      number=29, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='union_id', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.union_id', index=9,
      number=30, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='remark', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.remark', index=10,
      number=31, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='group_id', full_name='cf.wechat.UserInfoResponse.UserInfo.WxResult.group_id', index=11,
      number=32, type=5, cpp_type=1, label=1,
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
  serialized_start=1087,
  serialized_end=1309,
)

_USERINFORESPONSE_USERINFO = _descriptor.Descriptor(
  name='UserInfo',
  full_name='cf.wechat.UserInfoResponse.UserInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='wxerrcode', full_name='cf.wechat.UserInfoResponse.UserInfo.wxerrcode', index=0,
      number=10, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='wxresult', full_name='cf.wechat.UserInfoResponse.UserInfo.wxresult', index=1,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_USERINFORESPONSE_USERINFO_WXRESULT, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=990,
  serialized_end=1309,
)

_USERINFORESPONSE = _descriptor.Descriptor(
  name='UserInfoResponse',
  full_name='cf.wechat.UserInfoResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='errcode', full_name='cf.wechat.UserInfoResponse.errcode', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='errmsg', full_name='cf.wechat.UserInfoResponse.errmsg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='result', full_name='cf.wechat.UserInfoResponse.result', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_USERINFORESPONSE_USERINFO, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=882,
  serialized_end=1309,
)


_SYNCUSERINFOREQUEST = _descriptor.Descriptor(
  name='SyncUserInfoRequest',
  full_name='cf.wechat.SyncUserInfoRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='account_id', full_name='cf.wechat.SyncUserInfoRequest.account_id', index=0,
      number=10, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='customer_search_condition', full_name='cf.wechat.SyncUserInfoRequest.customer_search_condition', index=1,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='language', full_name='cf.wechat.SyncUserInfoRequest.language', index=2,
      number=12, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
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
  serialized_start=1312,
  serialized_end=1464,
)


_SYNCUSERINFORESPONSE = _descriptor.Descriptor(
  name='SyncUserInfoResponse',
  full_name='cf.wechat.SyncUserInfoResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='errcode', full_name='cf.wechat.SyncUserInfoResponse.errcode', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='errmsg', full_name='cf.wechat.SyncUserInfoResponse.errmsg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='openid_list', full_name='cf.wechat.SyncUserInfoResponse.openid_list', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='next_openid', full_name='cf.wechat.SyncUserInfoResponse.next_openid', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  serialized_start=1466,
  serialized_end=1563,
)


_GROUPMESSAGESENDREQUEST = _descriptor.Descriptor(
  name='GroupMessageSendRequest',
  full_name='cf.wechat.GroupMessageSendRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='account_id', full_name='cf.wechat.GroupMessageSendRequest.account_id', index=0,
      number=10, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='customer_search_condition', full_name='cf.wechat.GroupMessageSendRequest.customer_search_condition', index=1,
      number=13, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='group_id', full_name='cf.wechat.GroupMessageSendRequest.group_id', index=2,
      number=20, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='message_content', full_name='cf.wechat.GroupMessageSendRequest.message_content', index=3,
      number=14, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_record', full_name='cf.wechat.GroupMessageSendRequest.is_record', index=4,
      number=15, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  serialized_start=1566,
  serialized_end=1771,
)


_GROUPMESSAGESENDRESPONSE = _descriptor.Descriptor(
  name='GroupMessageSendResponse',
  full_name='cf.wechat.GroupMessageSendResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='errcode', full_name='cf.wechat.GroupMessageSendResponse.errcode', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='errmsg', full_name='cf.wechat.GroupMessageSendResponse.errmsg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='msg_id', full_name='cf.wechat.GroupMessageSendResponse.msg_id', index=2,
      number=3, type=5, cpp_type=1, label=1,
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
  serialized_start=1773,
  serialized_end=1848,
)


_MESSAGECONTENT = _descriptor.Descriptor(
  name='MessageContent',
  full_name='cf.wechat.MessageContent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='cf.wechat.MessageContent.type', index=0,
      number=10, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='resource_id', full_name='cf.wechat.MessageContent.resource_id', index=1,
      number=20, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='cf.wechat.MessageContent.content', index=2,
      number=30, type=9, cpp_type=9, label=1,
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
  serialized_start=1850,
  serialized_end=1941,
)

_MESSAGE.fields_by_name['header'].message_type = _HEADER
_MESSAGE.fields_by_name['req_group_message_send'].message_type = _GROUPMESSAGESENDREQUEST
_MESSAGE.fields_by_name['res_group_message_send'].message_type = _GROUPMESSAGESENDRESPONSE
_MESSAGE.fields_by_name['req_userinfo_query'].message_type = _USERINFOREQUEST
_MESSAGE.fields_by_name['res_userinfo_query'].message_type = _USERINFORESPONSE
_MESSAGE.fields_by_name['req_userinfo_sync'].message_type = _SYNCUSERINFOREQUEST
_MESSAGE.fields_by_name['res_userinfo_sync'].message_type = _SYNCUSERINFORESPONSE
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['req_group_message_send'])
_MESSAGE.fields_by_name['req_group_message_send'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['res_group_message_send'])
_MESSAGE.fields_by_name['res_group_message_send'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['req_userinfo_query'])
_MESSAGE.fields_by_name['req_userinfo_query'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['res_userinfo_query'])
_MESSAGE.fields_by_name['res_userinfo_query'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['req_userinfo_sync'])
_MESSAGE.fields_by_name['req_userinfo_sync'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_MESSAGE.oneofs_by_name['content'].fields.append(
  _MESSAGE.fields_by_name['res_userinfo_sync'])
_MESSAGE.fields_by_name['res_userinfo_sync'].containing_oneof = _MESSAGE.oneofs_by_name['content']
_USERINFOREQUEST.fields_by_name['customer_search_condition'].message_type = _CUSTOMERSEARCHCONDITION
_USERINFOREQUEST.fields_by_name['language'].enum_type = _ELANGUAGE
_USERINFORESPONSE_USERINFO_WXRESULT.containing_type = _USERINFORESPONSE_USERINFO
_USERINFORESPONSE_USERINFO.fields_by_name['wxresult'].message_type = _USERINFORESPONSE_USERINFO_WXRESULT
_USERINFORESPONSE_USERINFO.containing_type = _USERINFORESPONSE
_USERINFORESPONSE.fields_by_name['result'].message_type = _USERINFORESPONSE_USERINFO
_SYNCUSERINFOREQUEST.fields_by_name['customer_search_condition'].message_type = _CUSTOMERSEARCHCONDITION
_SYNCUSERINFOREQUEST.fields_by_name['language'].enum_type = _ELANGUAGE
_GROUPMESSAGESENDREQUEST.fields_by_name['customer_search_condition'].message_type = _CUSTOMERSEARCHCONDITION
_GROUPMESSAGESENDREQUEST.fields_by_name['message_content'].message_type = _MESSAGECONTENT
_MESSAGECONTENT.fields_by_name['type'].enum_type = _EMEDIATYPE
DESCRIPTOR.message_types_by_name['Header'] = _HEADER
DESCRIPTOR.message_types_by_name['Message'] = _MESSAGE
DESCRIPTOR.message_types_by_name['CustomerSearchCondition'] = _CUSTOMERSEARCHCONDITION
DESCRIPTOR.message_types_by_name['UserInfoRequest'] = _USERINFOREQUEST
DESCRIPTOR.message_types_by_name['UserInfoResponse'] = _USERINFORESPONSE
DESCRIPTOR.message_types_by_name['SyncUserInfoRequest'] = _SYNCUSERINFOREQUEST
DESCRIPTOR.message_types_by_name['SyncUserInfoResponse'] = _SYNCUSERINFORESPONSE
DESCRIPTOR.message_types_by_name['GroupMessageSendRequest'] = _GROUPMESSAGESENDREQUEST
DESCRIPTOR.message_types_by_name['GroupMessageSendResponse'] = _GROUPMESSAGESENDRESPONSE
DESCRIPTOR.message_types_by_name['MessageContent'] = _MESSAGECONTENT
DESCRIPTOR.enum_types_by_name['EMediaType'] = _EMEDIATYPE
DESCRIPTOR.enum_types_by_name['ELanguage'] = _ELANGUAGE

Header = _reflection.GeneratedProtocolMessageType('Header', (_message.Message,), dict(
  DESCRIPTOR = _HEADER,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.Header)
  ))
_sym_db.RegisterMessage(Header)

Message = _reflection.GeneratedProtocolMessageType('Message', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGE,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.Message)
  ))
_sym_db.RegisterMessage(Message)

CustomerSearchCondition = _reflection.GeneratedProtocolMessageType('CustomerSearchCondition', (_message.Message,), dict(
  DESCRIPTOR = _CUSTOMERSEARCHCONDITION,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.CustomerSearchCondition)
  ))
_sym_db.RegisterMessage(CustomerSearchCondition)

UserInfoRequest = _reflection.GeneratedProtocolMessageType('UserInfoRequest', (_message.Message,), dict(
  DESCRIPTOR = _USERINFOREQUEST,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.UserInfoRequest)
  ))
_sym_db.RegisterMessage(UserInfoRequest)

UserInfoResponse = _reflection.GeneratedProtocolMessageType('UserInfoResponse', (_message.Message,), dict(

  UserInfo = _reflection.GeneratedProtocolMessageType('UserInfo', (_message.Message,), dict(

    WxResult = _reflection.GeneratedProtocolMessageType('WxResult', (_message.Message,), dict(
      DESCRIPTOR = _USERINFORESPONSE_USERINFO_WXRESULT,
      __module__ = 'cf_wechat_pb2'
      # @@protoc_insertion_point(class_scope:cf.wechat.UserInfoResponse.UserInfo.WxResult)
      ))
    ,
    DESCRIPTOR = _USERINFORESPONSE_USERINFO,
    __module__ = 'cf_wechat_pb2'
    # @@protoc_insertion_point(class_scope:cf.wechat.UserInfoResponse.UserInfo)
    ))
  ,
  DESCRIPTOR = _USERINFORESPONSE,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.UserInfoResponse)
  ))
_sym_db.RegisterMessage(UserInfoResponse)
_sym_db.RegisterMessage(UserInfoResponse.UserInfo)
_sym_db.RegisterMessage(UserInfoResponse.UserInfo.WxResult)

SyncUserInfoRequest = _reflection.GeneratedProtocolMessageType('SyncUserInfoRequest', (_message.Message,), dict(
  DESCRIPTOR = _SYNCUSERINFOREQUEST,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.SyncUserInfoRequest)
  ))
_sym_db.RegisterMessage(SyncUserInfoRequest)

SyncUserInfoResponse = _reflection.GeneratedProtocolMessageType('SyncUserInfoResponse', (_message.Message,), dict(
  DESCRIPTOR = _SYNCUSERINFORESPONSE,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.SyncUserInfoResponse)
  ))
_sym_db.RegisterMessage(SyncUserInfoResponse)

GroupMessageSendRequest = _reflection.GeneratedProtocolMessageType('GroupMessageSendRequest', (_message.Message,), dict(
  DESCRIPTOR = _GROUPMESSAGESENDREQUEST,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.GroupMessageSendRequest)
  ))
_sym_db.RegisterMessage(GroupMessageSendRequest)

GroupMessageSendResponse = _reflection.GeneratedProtocolMessageType('GroupMessageSendResponse', (_message.Message,), dict(
  DESCRIPTOR = _GROUPMESSAGESENDRESPONSE,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.GroupMessageSendResponse)
  ))
_sym_db.RegisterMessage(GroupMessageSendResponse)

MessageContent = _reflection.GeneratedProtocolMessageType('MessageContent', (_message.Message,), dict(
  DESCRIPTOR = _MESSAGECONTENT,
  __module__ = 'cf_wechat_pb2'
  # @@protoc_insertion_point(class_scope:cf.wechat.MessageContent)
  ))
_sym_db.RegisterMessage(MessageContent)


# @@protoc_insertion_point(module_scope)
