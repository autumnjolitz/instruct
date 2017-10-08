from instruct import Base
from typing import Union
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput


class Data(Base):
    __slots__ = {
        'field': Union[str, int],
        'id': int,
        'name': str,
    }

    def __init__(self, **kwargs):
        self.field = 0
        self.id = 0
        self.name = ''
        super().__init__(**kwargs)


with PyCallGraph(output=GraphvizOutput(output_file='callgraph.png')):
    for i in range(1000):
        Data(field='name', id=123, name='ben')
