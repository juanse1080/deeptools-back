from .abstract import Element, File


class ServerElement(Element):
    def __init__(self, props, many_graph=False, many_series=False):
        super().__init__(**props)
        self.many_graph = many_graph
        self.many_series = many_series
        self.content = ''
        getattr(self, self._kind)()

    def output(self):

        content = 'def generate_outputs(outputs):\n\treturn objects.Outputs('
        if int(self._len) > 0:
            content += 'outputs=(objects.Output(value=output) for output in outputs))\n\n'
        else:
            content += 'outputs=objects.Output(value=outputs))\n\n'

        content += 'def outputs_data(outputs):\n'
        content += '\treturn outputs.value\n\n'
        self.content = content

    def input(self):
        content = 'def generate_inputs(inputs):\n\treturn objects.Inputs('
        if int(self._len) > 0:
            content += 'inputs=(objects.Input(value=input) for input in inputs))\n\n'
        else:
            content += 'inputs=objects.Input(value=inputs))\n\n'

        content += 'def inputs_data(inputs):\n'
        if int(self._len) > 0:
            content += '\treturn [input.value for input in inputs]\n\n'
        else:
            content += '\treturn inputs.value\n\n'
        self.content = content

    def response(self):
        content = 'def generate_responses(response):\n\treturn objects.Responses(value=response)\n\n'
        self.content = content

    def graph(self):
        content = 'def generate_serie(points):\n\treturn objects.Serie(points=(objects.Point(x=str(point[0]), y=str(point[1])) for point in points))\n\n'

        content += 'def generate_graph(graphs):\n\treturn objects.Graph(\n'
        if self.many_series:
            content += '\t\tseries=(generate_serie(graph) for graph in graphs))\n\n'
        else:
            content += '\t\tseries=generate_serie(graphs))\n\n'
        content += 'def generate_graph(graphs):\n\treturn objects.Graph(\n'
        if self.many_graph:
            content += '\t\tseries=(generate_serie(graph) for graph in graphs))\n\n'
        else:
            content += '\t\tseries=generate_serie(graphs))\n\n'
        self.content = content


class ServerFile(File):
    def __init__(self, items):
        super().__init__(items=items, field=ServerElement)

    def build_elements(self):
        self.content += 'def data_return(class__):\n\treturn objects.Elements(\n'
        for elem in self.elements:
            self.content += '\t\t{0}s=generate_{0}s(class__.{0}__),\n'.format(
                elem._kind)
        self.content += '\t)\n\n'

    def build_in(self):
        self.content += 'def in_data(data):\n\treturn (\n\t\tinputs_data(data.inputs.inputs),\n'
        if self._have_outputs:
            self.content += '\t\toutputs_data(data.output),\n'
        self.content += '\t)\n\n'

    def create_server(self, id, file, workdir, class__):
        self.content += 'import grpc\nfrom concurrent import futures\nimport time\nimport sys\nsys.path.insert(0, "{2}/{0}")\nfrom {0} import protobuf_pb2 as objects\nfrom {0} import protobuf_pb2_grpc as services\nimport {1}\n_ONE_DAY_IN_SECONDS = 60 * 60 * 24\n\n'.format(
            id, file, workdir)

        self.get_content()
        self.build_in()
        self.build_elements()

        self.content += 'class ServerServicer(services.ServerServicer):\n\tdef execute(self, request, context):\n\t\tclass_ = {0}.{1}(*in_data(request))\n\t\tstate = class_.state__\n\t\twith futures.ThreadPoolExecutor(max_workers=1) as executor:\n\t\t\tfuture = executor.submit(class_.run)\n\t\t\twhile future.running():\n\t\t\t\tif state != class_.state__:\n\t\t\t\t\tstate = class_.state__\n\t\t\t\t\tyield objects.Return(\n\t\t\t\t\t\tstate=objects.State(\n\t\t\t\t\t\t\tvalue=str(class_.state__),\n\t\t\t\t\t\t\tdescription=class_.description__\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\tfuture.result()\n\t\tyield objects.Return(\n\t\t\tstate=objects.State(\n\t\t\t\tvalue=str(class_.state__),\n\t\t\t\tdescription=class_.description__\n\t\t\t),\n\t\t\telements=data_return(class_)\n\t\t)\n\ndef serve():\n\tserver = grpc.server(futures.ThreadPoolExecutor(max_workers=1000))\n\tservices.add_ServerServicer_to_server(ServerServicer(), server)\n\tserver.add_insecure_port("[::]:50051")\n\tserver.start()\n\ttry:\n\t\twhile True:\n\t\t\ttime.sleep(_ONE_DAY_IN_SECONDS)\n\texcept KeyboardInterrupt:\n\t\tserver.stop(0)\nif __name__ == "__main__":\n\tserve()\n'.format(
            file, class__)

        return self.content
