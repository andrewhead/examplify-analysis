import logging
from peewee import fn

from dump.dump import dump_csv
from models import DefinitionCorrection


logger = logging.getLogger('data')


@dump_csv(__name__, [
    "Compute Index", "Participant", "Time", "Symbol Name", "Correction Type"])
def main(compute_index, *args, **kwargs):

    if not compute_index:
        compute_index = DefinitionCorrection.select(
            fn.Max(DefinitionCorrection.compute_index)).scalar()

    for correction in DefinitionCorrection.select(
            DefinitionCorrection.compute_index,
            DefinitionCorrection.participant_id,
            DefinitionCorrection.symbol_name,
            DefinitionCorrection.correction_type,
            DefinitionCorrection.time,
            fn.Max(DefinitionCorrection.time).alias("time")
        ).where(
            DefinitionCorrection.compute_index == compute_index
        ).group_by(
            DefinitionCorrection.participant_id,
            DefinitionCorrection.symbol_name,
        ):
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
    parser.add_argument(
        "--compute_index",
        type=int,
        help="Index of round of computation that corrections came from."
    )
