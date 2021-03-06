# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: holoViveCom.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='holoViveCom.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x11holoViveCom.proto\"\x18\n\x06Status\x12\x0e\n\x06status\x18\x01 \x01(\t\"\x07\n\x05\x45mpty\"x\n\x0fLighthouseState\x12\x1d\n\x0bholoTracker\x18\x01 \x01(\x0b\x32\x08.Tracker\x12\x1d\n\x0b\x63\x61liTracker\x18\x02 \x01(\x0b\x32\x08.Tracker\x12\'\n\ncontroller\x18\x03 \x01(\x0b\x32\x13.HandheldController\"L\n\x0cTrackerState\x12\x1d\n\x0bholoTracker\x18\x01 \x01(\x0b\x32\x08.Tracker\x12\x1d\n\x0b\x63\x61liTracker\x18\x02 \x01(\x0b\x32\x08.Tracker\"F\n\x07Tracker\x12\n\n\x02ID\x18\x01 \x01(\t\x12\x1d\n\x08rotation\x18\x02 \x01(\x0b\x32\x0b.Quaternion\x12\x10\n\x08position\x18\x03 \x03(\x02\"\xc1\x01\n\x12HandheldController\x12\n\n\x02ID\x18\x01 \x01(\t\x12\x1d\n\x08rotation\x18\x02 \x01(\x0b\x32\x0b.Quaternion\x12\x10\n\x08position\x18\x03 \x03(\x02\x12:\n\x0c\x62utton_state\x18\x04 \x03(\x0b\x32$.HandheldController.ButtonStateEntry\x1a\x32\n\x10\x42uttonStateEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\x1a\n\nQuaternion\x12\x0c\n\x04quat\x18\x01 \x03(\x02\"D\n\x0f\x43\x61librationInfo\x12\x0e\n\x06status\x18\x01 \x01(\t\x12!\n\x19\x63\x61librationMatrixRowMajor\x18\x02 \x03(\x02\x32\xf4\x01\n\x07\x42\x61\x63kend\x12\x30\n\x10LighthouseReport\x12\x10.LighthouseState\x1a\x06.Empty\"\x00(\x01\x12-\n\x12ProvideTrackerInfo\x12\x06.Empty\x1a\r.TrackerState\"\x00\x12!\n\x0c\x43hangeStatus\x12\x07.Status\x1a\x06.Empty\"\x00\x12\x33\n\x15UpdateCalibrationInfo\x12\x10.CalibrationInfo\x1a\x06.Empty\"\x00\x12\x30\n\x12GetCalibrationInfo\x12\x06.Empty\x1a\x10.CalibrationInfo\"\x00\x62\x06proto3'
)




_STATUS = _descriptor.Descriptor(
  name='Status',
  full_name='Status',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='Status.status', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=45,
)


_EMPTY = _descriptor.Descriptor(
  name='Empty',
  full_name='Empty',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=47,
  serialized_end=54,
)


_LIGHTHOUSESTATE = _descriptor.Descriptor(
  name='LighthouseState',
  full_name='LighthouseState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='holoTracker', full_name='LighthouseState.holoTracker', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='caliTracker', full_name='LighthouseState.caliTracker', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='controller', full_name='LighthouseState.controller', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=56,
  serialized_end=176,
)


_TRACKERSTATE = _descriptor.Descriptor(
  name='TrackerState',
  full_name='TrackerState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='holoTracker', full_name='TrackerState.holoTracker', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='caliTracker', full_name='TrackerState.caliTracker', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=178,
  serialized_end=254,
)


_TRACKER = _descriptor.Descriptor(
  name='Tracker',
  full_name='Tracker',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ID', full_name='Tracker.ID', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rotation', full_name='Tracker.rotation', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='position', full_name='Tracker.position', index=2,
      number=3, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=256,
  serialized_end=326,
)


_HANDHELDCONTROLLER_BUTTONSTATEENTRY = _descriptor.Descriptor(
  name='ButtonStateEntry',
  full_name='HandheldController.ButtonStateEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='HandheldController.ButtonStateEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='HandheldController.ButtonStateEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=472,
  serialized_end=522,
)

_HANDHELDCONTROLLER = _descriptor.Descriptor(
  name='HandheldController',
  full_name='HandheldController',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ID', full_name='HandheldController.ID', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rotation', full_name='HandheldController.rotation', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='position', full_name='HandheldController.position', index=2,
      number=3, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='button_state', full_name='HandheldController.button_state', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_HANDHELDCONTROLLER_BUTTONSTATEENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=329,
  serialized_end=522,
)


_QUATERNION = _descriptor.Descriptor(
  name='Quaternion',
  full_name='Quaternion',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='quat', full_name='Quaternion.quat', index=0,
      number=1, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=524,
  serialized_end=550,
)


_CALIBRATIONINFO = _descriptor.Descriptor(
  name='CalibrationInfo',
  full_name='CalibrationInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='CalibrationInfo.status', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='calibrationMatrixRowMajor', full_name='CalibrationInfo.calibrationMatrixRowMajor', index=1,
      number=2, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=552,
  serialized_end=620,
)

_LIGHTHOUSESTATE.fields_by_name['holoTracker'].message_type = _TRACKER
_LIGHTHOUSESTATE.fields_by_name['caliTracker'].message_type = _TRACKER
_LIGHTHOUSESTATE.fields_by_name['controller'].message_type = _HANDHELDCONTROLLER
_TRACKERSTATE.fields_by_name['holoTracker'].message_type = _TRACKER
_TRACKERSTATE.fields_by_name['caliTracker'].message_type = _TRACKER
_TRACKER.fields_by_name['rotation'].message_type = _QUATERNION
_HANDHELDCONTROLLER_BUTTONSTATEENTRY.containing_type = _HANDHELDCONTROLLER
_HANDHELDCONTROLLER.fields_by_name['rotation'].message_type = _QUATERNION
_HANDHELDCONTROLLER.fields_by_name['button_state'].message_type = _HANDHELDCONTROLLER_BUTTONSTATEENTRY
DESCRIPTOR.message_types_by_name['Status'] = _STATUS
DESCRIPTOR.message_types_by_name['Empty'] = _EMPTY
DESCRIPTOR.message_types_by_name['LighthouseState'] = _LIGHTHOUSESTATE
DESCRIPTOR.message_types_by_name['TrackerState'] = _TRACKERSTATE
DESCRIPTOR.message_types_by_name['Tracker'] = _TRACKER
DESCRIPTOR.message_types_by_name['HandheldController'] = _HANDHELDCONTROLLER
DESCRIPTOR.message_types_by_name['Quaternion'] = _QUATERNION
DESCRIPTOR.message_types_by_name['CalibrationInfo'] = _CALIBRATIONINFO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Status = _reflection.GeneratedProtocolMessageType('Status', (_message.Message,), {
  'DESCRIPTOR' : _STATUS,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:Status)
  })
_sym_db.RegisterMessage(Status)

Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:Empty)
  })
_sym_db.RegisterMessage(Empty)

LighthouseState = _reflection.GeneratedProtocolMessageType('LighthouseState', (_message.Message,), {
  'DESCRIPTOR' : _LIGHTHOUSESTATE,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:LighthouseState)
  })
_sym_db.RegisterMessage(LighthouseState)

TrackerState = _reflection.GeneratedProtocolMessageType('TrackerState', (_message.Message,), {
  'DESCRIPTOR' : _TRACKERSTATE,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:TrackerState)
  })
_sym_db.RegisterMessage(TrackerState)

Tracker = _reflection.GeneratedProtocolMessageType('Tracker', (_message.Message,), {
  'DESCRIPTOR' : _TRACKER,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:Tracker)
  })
_sym_db.RegisterMessage(Tracker)

HandheldController = _reflection.GeneratedProtocolMessageType('HandheldController', (_message.Message,), {

  'ButtonStateEntry' : _reflection.GeneratedProtocolMessageType('ButtonStateEntry', (_message.Message,), {
    'DESCRIPTOR' : _HANDHELDCONTROLLER_BUTTONSTATEENTRY,
    '__module__' : 'holoViveCom_pb2'
    # @@protoc_insertion_point(class_scope:HandheldController.ButtonStateEntry)
    })
  ,
  'DESCRIPTOR' : _HANDHELDCONTROLLER,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:HandheldController)
  })
_sym_db.RegisterMessage(HandheldController)
_sym_db.RegisterMessage(HandheldController.ButtonStateEntry)

Quaternion = _reflection.GeneratedProtocolMessageType('Quaternion', (_message.Message,), {
  'DESCRIPTOR' : _QUATERNION,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:Quaternion)
  })
_sym_db.RegisterMessage(Quaternion)

CalibrationInfo = _reflection.GeneratedProtocolMessageType('CalibrationInfo', (_message.Message,), {
  'DESCRIPTOR' : _CALIBRATIONINFO,
  '__module__' : 'holoViveCom_pb2'
  # @@protoc_insertion_point(class_scope:CalibrationInfo)
  })
_sym_db.RegisterMessage(CalibrationInfo)


_HANDHELDCONTROLLER_BUTTONSTATEENTRY._options = None

_BACKEND = _descriptor.ServiceDescriptor(
  name='Backend',
  full_name='Backend',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=623,
  serialized_end=867,
  methods=[
  _descriptor.MethodDescriptor(
    name='LighthouseReport',
    full_name='Backend.LighthouseReport',
    index=0,
    containing_service=None,
    input_type=_LIGHTHOUSESTATE,
    output_type=_EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ProvideTrackerInfo',
    full_name='Backend.ProvideTrackerInfo',
    index=1,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_TRACKERSTATE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ChangeStatus',
    full_name='Backend.ChangeStatus',
    index=2,
    containing_service=None,
    input_type=_STATUS,
    output_type=_EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='UpdateCalibrationInfo',
    full_name='Backend.UpdateCalibrationInfo',
    index=3,
    containing_service=None,
    input_type=_CALIBRATIONINFO,
    output_type=_EMPTY,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='GetCalibrationInfo',
    full_name='Backend.GetCalibrationInfo',
    index=4,
    containing_service=None,
    input_type=_EMPTY,
    output_type=_CALIBRATIONINFO,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_BACKEND)

DESCRIPTOR.services_by_name['Backend'] = _BACKEND

# @@protoc_insertion_point(module_scope)
