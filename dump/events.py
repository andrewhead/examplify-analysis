import logging
import json

from dump.dump import dump_csv
from models import Event


logger = logging.getLogger('data')


@dump_csv(__name__, [
    "Import Index", "Participant", "Time", "Tool", "Event Type", "JSON Data"],
    delimiter="|")
def main(*args, **kwargs):

    for event in Event.select():
        
        yield [[
            event.import_index,
            event.participant_id,
            event.time,
            event.tool,
            event.label,
            event.data,
        ]]

    raise StopIteration


def configure_parser(parser):
    parser.description = "Dump full event log."
