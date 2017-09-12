import logging

from dump.dump import dump_csv
from models import Choice


logger = logging.getLogger('data')


@dump_csv(__name__, [
    "Compute Index", "Participant", "Time", "Accepted", "Extension Type"])
def main(*args, **kwargs):

    for choice in Choice.select():
        
        yield [[
            choice.compute_index,
            choice.participant_id,
            choice.time,
            choice.accepted,
            choice.extension_type,
        ]]

    raise StopIteration


def configure_parser(parser):
    parser.description = "Dump records of choices about extensions."
