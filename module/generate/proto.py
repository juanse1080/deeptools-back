from .abstract import Element, File


class ProtoElement(Element):
    def __init__(self, props, many_graph=False, many_series=False):
        super().__init__(**props)
        self.many_graph = many_graph
        self.many_series = many_series
        self.content = ''
        getattr(self, self._kind)()

    def output(self):
        content = '// ----------- Output message ---------- \n\n'
        content += 'message Output {\n\tstring value = 1;\n}\n\n'
        content += 'message Outputs {\n\t'
        if int(self._len) > 0:
            content += 'repeated '

        content += 'Output outputs = 1;\n}\n\n'
        self.content = content

    def input(self):
        content = '// ----------- Input message ---------- \n\n'
        content += 'message Input {\n\tstring value = 1;\n}\n\n'
        content += 'message Inputs {\n\t'
        if int(self._len) > 0:
            content += 'repeated '
        content += 'Input inputs = 1;\n}\n\n'
        self.content = content

    def response(self):
        content = '// ----------- Response message --------- \n\nmessage Responses {\n\tstring value = 1;\n}\n\n'
        self.content = content

    def graph(self):
        content = '// ----------- Graph message ---------- \n\nmessage Point {\n\tstring x = 1;\n\tstring y = 2;\n}\n\nmessage Serie {\n\trepeated Point points = 1;\n}\n\n'

        content += 'message Graph {\n\t'
        if self.many_series:
            content += 'repeated '
        content += 'Serie series = 1;\n}\n\n'

        content += 'message Graphs {\n\t'
        if self.many_graph:
            content += 'repeated '
        content += 'Graph graphs = 1;\n}\n\n'
        self.content = content


class ProtoFile(File):
    def __init__(self, items):
        super().__init__(items=items, field=ProtoElement)

    def build_elements(self):
        self.content += '// ----------- Elements message ------------\n\nmessage Elements {\n'
        for index, elem in enumerate(self.elements):
            self.content += '\t{0}s {1}s = {2};\n'.format(
                elem._kind.title(), elem._kind, index + 1)
        self.content += '}\n\n'

    def build_in(self):
        self.content += '// ----------- In message ------------\n\nmessage In {\n\tInputs inputs = 1;\n'
        if self._have_outputs:
            self.content += '\tOutput output = 2;\n'
        self.content += '}\n\n'

    def create_protobuf(self):
        self.content += 'syntax = "proto3"; \n\n'
        self.content += '// ----------- Server service ------------\n\nservice Server {\n\trpc execute(In) returns (stream Return);\n}\n\n'
        self.content += '// ----------- State message ------------\n\nmessage State {\n\tstring value = 1;\n\tstring description = 2;\n}\n\n'
        self.content += '// ----------- Return message ------------\n\nmessage Return {\n\tState state = 1;\n\tElements elements = 2;\n}\n\n'

        self.get_content()
        self.build_elements()
        self.build_in()

        return self.content
