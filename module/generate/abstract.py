class Element:
    def __init__(self, **kwargs):
        for attr in kwargs:
            setattr(self, '_{0}'.format(attr), kwargs[attr])


class File:
    def __init__(self, items, field):
        self.items = items
        self.field = field
        self.elements = []
        self.content = ''
        self._have_outputs = False
        self.build_file()

    def build_file(self):
        temp = []
        many_graph = 0
        flag_series = False
        for i in self.items:
            if i["kind"] == "output":
                self._have_outputs = True
            if i["kind"] == "graph":
                many_graph += 1
                many_series = True if int(
                    i["len"]) > 0 or flag_series else False
                flag_series = many_series
            else:
                temp.append(i)

        for element in temp:
            self.elements.append(self.field(element))

        if many_graph > 0:
            self.elements.append(
                self.field(
                    {'kind': 'graph', 'len': '1'}, many_series=flag_series, many_graph=True if many_graph > 1 else False)
            )

    def get_content(self):
        for element in self.elements:
            self.content += element.content
        return self.content
