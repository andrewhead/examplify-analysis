import logging

from dump.dump import dump_csv
from models import DefinitionCorrection


logger = logging.getLogger('data')


@dump_csv(__name__, [
    "Compute Index", "Participant", "Time", "Symbol Name", "Correction Type"])
def main(*args, **kwargs):

    for correction in DefinitionCorrection.select():
        yield [[
            correction.compute_index,
            correction.participant_id,
            correction.time,
            correction.symbol_name,
            correction.correction_type,
        ]]

    raise StopIteration


def configure_parser(parser):
    parser.description = "Dump records of choices about corrections made to define symbols."
