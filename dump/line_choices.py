import logging

from dump.dump import dump_csv
from models import LineChoice


logger = logging.getLogger('data')


@dump_csv(__name__, [
    "Compute Index", "Participant", "Time", "Line Number"])
def main(*args, **kwargs):

    for choice in LineChoice.select():
        
        yield [[
            choice.compute_index,
            choice.participant_id,
            choice.time,
            choice.line_number,
        ]]

    raise StopIteration


def configure_parser(parser):
    parser.description = "Dump records of choices of line numbers."
