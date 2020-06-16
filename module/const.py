MESSAGES = {
    'graph': '// ----------- Graph message ---------- \n\nmessage Point {\n\tstring x = 1;\n\tstring y = 2;\n}\n\nmessage Serie {\n\trepeated Point points = 1;\n}\n\nmessage Graph {\n\trepeated Serie series = 1;\n}\n\nmessage Graphs {\n\trepeated Graph values = 1;\n}\n\n',
    'response': '// ----------- Response message - --------\n\nmessage Response {\n\tstring value = 1;\n}\n\n',
    'input': '// ----------- Input message - -----------\n\nmessage Media {\n\tstring url = 1;\n}\n\nmessage Input {\n\trepeated Media values = 1;\n}\n\n',
    'output': '// ----------- Output message - -----------\n\nmessage Output {\n\trepeated Media values = 1;\n}\n\n',
}

PROTO = 'syntax = "proto3"; \n\n'

STATE = '// ----------- State message - -----------\n\nmessage State {\n\tstring value = 1;\n\tstring description = 2;\n}\n\n'

BLANK = '// ----------- Blank message - -----------\n\nmessage Blank {}\n\n'

SERVER = '// ----------- Server service - -----------\n\nservice Server {\n\trpc execute(Input) returns (stream Return);\n}\n\n'

RETURN = '// ----------- Return message - -----------\n\nmessage Return {\n\State state = 1;\n\tElements elements = 2;\n}\n\n'

INIT_ELEMENTS = '// ----------- ELements message - -----------\n\nmessage Elements {\n'

AUX = '}\n\n'

HAVE_ELEMENTS = {
    'input': '\tInput input = {0};\n',
    'output': '\tOutput output = {0};\n',
    'response': '\tResponse response = {0};\n',
    'graph': '\tGraphs graph = {0};\n',
}


def generate_protobuf(elements):
    response = PROTO
    response += SERVER

    for element in elements:
        response += MESSAGES[element]

    response += BLANK
    response += STATE
    response += INIT_ELEMENTS

    for item, element in enumerate(elements):
        response += HAVE_ELEMENTS[element].format(item + 1)

    response += AUX
    response += RETURN
    return response
