import logging

from dump.dump import dump_csv
from models import VcodeEvent


logger = logging.getLogger('data')


@dump_csv(__name__, [
    "Import Index", "Participant", "Tool", "Task Time (minutes)", "Finished"])
def main(*args, **kwargs):

    for event in VcodeEvent.select().where(VcodeEvent.label.contains("Example")):

        tool_name = event.label.split(" ")[0]
        yield [[
            event.import_index,
            event.participant_id,
            tool_name,
            float(event.length_ms) / 1000 / 60,
            event.data,
        ]]

    raise StopIteration


def configure_parser(parser):
    parser.description="Dump records of how long tasks took."
