"""Set of handlers related with Flowcells
"""

import tornado.web
import json

from collections import OrderedDict


class FlowcellsHandler(tornado.web.RequestHandler):
    """ Serves a page which lists all flowcells with some brief info.
    """
    def get(self):
        t = self.application.loader.load("flowcells.html")
        self.write(t.generate())


class FlowcellHandler(tornado.web.RequestHandler):
    """ Serves a page which shows information and QC stats for a given
    flowcell.
    """
    def get(self, flowcell):
        t = self.application.loader.load("flowcell_samples.html")
        self.write(t.generate(flowcell=flowcell))


class FlowcellsDataHandler(tornado.web.RequestHandler):
    """ Serves brief information for each flowcell in the database.
    """
    def get(self):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.list_flowcells()))

    def list_flowcells(self):
        flowcells = OrderedDict()
        fc_view = self.application.flowcells_db.view("info/summary",
                                                     descending=True)
        for row in fc_view:
            flowcells[row.key] = row.value

        return flowcells


class FlowcellsInfoDataHandler(tornado.web.RequestHandler):
    """ Serves brief information about a given flowcell.
    """
    def get(self, flowcell):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.flowcell_info(flowcell)))

    def flowcell_info(self, flowcell):
        fc_view = self.application.flowcells_db.view("info/summary",
                                                     descending=True)
        for row in fc_view[flowcell]:
            flowcell_info = row.value
            break

        return flowcell_info


class FlowcellDataHandler(tornado.web.RequestHandler):
    """ Serves a list of sample runs in a flowcell.
    """
    def get(self, flowcell):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.list_sample_runs(flowcell)))

    def list_sample_runs(self, flowcell):
        sample_run_list = []
        fc_view = self.application.samples_db.view("flowcell/name", reduce=False)
        for row in fc_view[flowcell]:
            sample_run_list.append(row.value)

        return sample_run_list


class FlowcellQCHandler(tornado.web.RequestHandler):
    """ Serves QC data for each lane in a given flowcell.
    """
    def get(self, flowcell):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.list_sample_runs(flowcell)))

    def list_sample_runs(self, flowcell):
        lane_qc = OrderedDict()
        lane_view = self.application.flowcells_db.view("lanes/qc")
        for row in lane_view[[flowcell, ""]:[flowcell, "Z"]]:
            lane_qc[row.key[1]] = row.value

        return lane_qc


class FlowcellDemultiplexHandler(tornado.web.RequestHandler):
    """ Serves demultiplex yield data for each lane in a given flowcell.
    """
    def get(self, flowcell):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.lane_stats(flowcell)))

    def lane_stats(self, flowcell):
        lane_qc = OrderedDict()
        lane_view = self.application.flowcells_db.view("lanes/demultiplex")
        for row in lane_view[[flowcell, ""]:[flowcell, "Z"]]:
            lane_qc[row.key[1]] = row.value

        return lane_qc


class FlowcellQ30Handler(tornado.web.RequestHandler):
    """ Serves the percentage ofr reads over Q30 for each lane in the given
    flowcell.
    """
    def get(self, flowcell):
        self.set_header("Content-type", "application/json")
        self.write(json.dumps(self.lane_q30(flowcell)))

    def lane_q30(self, flowcell):
        lane_q30 = OrderedDict()
        lane_view = self.application.flowcells_db.view("lanes/gtq30", group_level=2)
        for row in lane_view[[flowcell, ""]:[flowcell, "Z"]]:
            lane_q30[row.key[1]] = row.value["sum"] / row.value["count"]

        return lane_q30