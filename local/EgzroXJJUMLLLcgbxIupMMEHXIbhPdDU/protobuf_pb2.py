# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU/protobuf.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU/protobuf.proto',
  package='egzroxjjumlllcgbxiupmmehxibhpddu',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n/EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU/protobuf.proto\x12 egzroxjjumlllcgbxiupmmehxibhpddu\"+\n\x05State\x12\r\n\x05value\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\"~\n\x06Return\x12\x36\n\x05state\x18\x01 \x01(\x0b\x32\'.egzroxjjumlllcgbxiupmmehxibhpddu.State\x12<\n\x08\x65lements\x18\x02 \x01(\x0b\x32*.egzroxjjumlllcgbxiupmmehxibhpddu.Elements\"\x16\n\x05Input\x12\r\n\x05value\x18\x01 \x01(\t\"A\n\x06Inputs\x12\x37\n\x06inputs\x18\x01 \x01(\x0b\x32\'.egzroxjjumlllcgbxiupmmehxibhpddu.Input\"\x1a\n\tResponses\x12\r\n\x05value\x18\x01 \x01(\t\"\x17\n\x06Output\x12\r\n\x05value\x18\x01 \x01(\t\"D\n\x07Outputs\x12\x39\n\x07outputs\x18\x01 \x01(\x0b\x32(.egzroxjjumlllcgbxiupmmehxibhpddu.Output\"\xc0\x01\n\x08\x45lements\x12\x38\n\x06inputs\x18\x01 \x01(\x0b\x32(.egzroxjjumlllcgbxiupmmehxibhpddu.Inputs\x12>\n\tresponses\x18\x02 \x01(\x0b\x32+.egzroxjjumlllcgbxiupmmehxibhpddu.Responses\x12:\n\x07outputs\x18\x03 \x01(\x0b\x32).egzroxjjumlllcgbxiupmmehxibhpddu.Outputs\"x\n\x02In\x12\x38\n\x06inputs\x18\x01 \x01(\x0b\x32(.egzroxjjumlllcgbxiupmmehxibhpddu.Inputs\x12\x38\n\x06output\x18\x02 \x01(\x0b\x32(.egzroxjjumlllcgbxiupmmehxibhpddu.Output2e\n\x06Server\x12[\n\x07\x65xecute\x12$.egzroxjjumlllcgbxiupmmehxibhpddu.In\x1a(.egzroxjjumlllcgbxiupmmehxibhpddu.Return0\x01\x62\x06proto3'
)




_STATE = _descriptor.Descriptor(
  name='State',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.State',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.State.value', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='description', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.State.description', index=1,
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=85,
  serialized_end=128,
)


_RETURN = _descriptor.Descriptor(
  name='Return',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Return',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='state', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Return.state', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='elements', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Return.elements', index=1,
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
  serialized_start=130,
  serialized_end=256,
)


_INPUT = _descriptor.Descriptor(
  name='Input',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Input',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Input.value', index=0,
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
  serialized_start=258,
  serialized_end=280,
)


_INPUTS = _descriptor.Descriptor(
  name='Inputs',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Inputs',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='inputs', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Inputs.inputs', index=0,
      number=1, type=11, cpp_type=10, label=1,
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
  serialized_start=282,
  serialized_end=347,
)


_RESPONSES = _descriptor.Descriptor(
  name='Responses',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Responses',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Responses.value', index=0,
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
  serialized_start=349,
  serialized_end=375,
)


_OUTPUT = _descriptor.Descriptor(
  name='Output',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Output',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='value', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Output.value', index=0,
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
  serialized_start=377,
  serialized_end=400,
)


_OUTPUTS = _descriptor.Descriptor(
  name='Outputs',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Outputs',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='outputs', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Outputs.outputs', index=0,
      number=1, type=11, cpp_type=10, label=1,
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
  serialized_start=402,
  serialized_end=470,
)


_ELEMENTS = _descriptor.Descriptor(
  name='Elements',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Elements',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='inputs', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Elements.inputs', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='responses', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Elements.responses', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='outputs', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Elements.outputs', index=2,
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
  serialized_start=473,
  serialized_end=665,
)


_IN = _descriptor.Descriptor(
  name='In',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.In',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='inputs', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.In.inputs', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='output', full_name='egzroxjjumlllcgbxiupmmehxibhpddu.In.output', index=1,
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
  serialized_start=667,
  serialized_end=787,
)

_RETURN.fields_by_name['state'].message_type = _STATE
_RETURN.fields_by_name['elements'].message_type = _ELEMENTS
_INPUTS.fields_by_name['inputs'].message_type = _INPUT
_OUTPUTS.fields_by_name['outputs'].message_type = _OUTPUT
_ELEMENTS.fields_by_name['inputs'].message_type = _INPUTS
_ELEMENTS.fields_by_name['responses'].message_type = _RESPONSES
_ELEMENTS.fields_by_name['outputs'].message_type = _OUTPUTS
_IN.fields_by_name['inputs'].message_type = _INPUTS
_IN.fields_by_name['output'].message_type = _OUTPUT
DESCRIPTOR.message_types_by_name['State'] = _STATE
DESCRIPTOR.message_types_by_name['Return'] = _RETURN
DESCRIPTOR.message_types_by_name['Input'] = _INPUT
DESCRIPTOR.message_types_by_name['Inputs'] = _INPUTS
DESCRIPTOR.message_types_by_name['Responses'] = _RESPONSES
DESCRIPTOR.message_types_by_name['Output'] = _OUTPUT
DESCRIPTOR.message_types_by_name['Outputs'] = _OUTPUTS
DESCRIPTOR.message_types_by_name['Elements'] = _ELEMENTS
DESCRIPTOR.message_types_by_name['In'] = _IN
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

State = _reflection.GeneratedProtocolMessageType('State', (_message.Message,), {
  'DESCRIPTOR' : _STATE,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.State)
  })
_sym_db.RegisterMessage(State)

Return = _reflection.GeneratedProtocolMessageType('Return', (_message.Message,), {
  'DESCRIPTOR' : _RETURN,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Return)
  })
_sym_db.RegisterMessage(Return)

Input = _reflection.GeneratedProtocolMessageType('Input', (_message.Message,), {
  'DESCRIPTOR' : _INPUT,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Input)
  })
_sym_db.RegisterMessage(Input)

Inputs = _reflection.GeneratedProtocolMessageType('Inputs', (_message.Message,), {
  'DESCRIPTOR' : _INPUTS,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Inputs)
  })
_sym_db.RegisterMessage(Inputs)

Responses = _reflection.GeneratedProtocolMessageType('Responses', (_message.Message,), {
  'DESCRIPTOR' : _RESPONSES,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Responses)
  })
_sym_db.RegisterMessage(Responses)

Output = _reflection.GeneratedProtocolMessageType('Output', (_message.Message,), {
  'DESCRIPTOR' : _OUTPUT,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Output)
  })
_sym_db.RegisterMessage(Output)

Outputs = _reflection.GeneratedProtocolMessageType('Outputs', (_message.Message,), {
  'DESCRIPTOR' : _OUTPUTS,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Outputs)
  })
_sym_db.RegisterMessage(Outputs)

Elements = _reflection.GeneratedProtocolMessageType('Elements', (_message.Message,), {
  'DESCRIPTOR' : _ELEMENTS,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.Elements)
  })
_sym_db.RegisterMessage(Elements)

In = _reflection.GeneratedProtocolMessageType('In', (_message.Message,), {
  'DESCRIPTOR' : _IN,
  '__module__' : 'EgzroXJJUMLLLcgbxIupMMEHXIbhPdDU.protobuf_pb2'
  # @@protoc_insertion_point(class_scope:egzroxjjumlllcgbxiupmmehxibhpddu.In)
  })
_sym_db.RegisterMessage(In)



_SERVER = _descriptor.ServiceDescriptor(
  name='Server',
  full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Server',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=789,
  serialized_end=890,
  methods=[
  _descriptor.MethodDescriptor(
    name='execute',
    full_name='egzroxjjumlllcgbxiupmmehxibhpddu.Server.execute',
    index=0,
    containing_service=None,
    input_type=_IN,
    output_type=_RETURN,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_SERVER)

DESCRIPTOR.services_by_name['Server'] = _SERVER

# @@protoc_insertion_point(module_scope)
