import base64
from abc import abstractmethod
from io import BytesIO

import music21

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class PlotRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')

        x_axis = node.data.get('xAxis')
        y_axis = node.data.get('yAxis')

        if in_0 is not None:
            output = self.plot(in_0, x_axis=x_axis, y_axis=y_axis)
            figure_buffer = BytesIO()
            output.figure.savefig(figure_buffer, format='svg')
            figure_buffer.seek(0)
            output_data['plot'] = base64.b64encode(figure_buffer.read())
            figure_buffer.close()

    @abstractmethod
    def plot(self, in_0: music21.stream, x_axis: str, y_axis: str):
        pass


class PlotBarRepository(PlotRepository):

    def plot(self, in_0, x_axis, y_axis):
        return in_0.plot('bar', x_axis, y_axis, doneAction=None)


class PlotBarWeightedRepository(PlotRepository):
    def plot(self, in_0, x_axis, y_axis):
        return in_0.plot('barweighted', x_axis, y_axis, doneAction=None)


class PlotHistogramRepository(PlotRepository):
    def plot(self, in_0, x_axis, y_axis):
        return in_0.plot('histogram', x_axis, doneAction=None)


class PlotScatterRepository(PlotRepository):
    def plot(self, in_0, x_axis, y_axis):
        return in_0.plot('scatter', x_axis, y_axis, doneAction=None)


class PlotScatterWeightedRepository(PlotRepository):
    def plot(self, in_0, x_axis, y_axis):
        return in_0.plot('scatterweighted', x_axis, y_axis, doneAction=None)
