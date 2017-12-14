from peewee import fn
import json

from models import Event, DefinitionCorrection


DEFINITION_CORRECTION_TYPES = [
    "DefinitionSuggestion",
    "PrimitiveValueSuggestion",
]


def main(event_import_index=None, *args, **kwargs):

    last_compute_index = DefinitionCorrection.select(
        fn.Max(DefinitionCorrection.compute_index)).scalar() or 0
    compute_index = last_compute_index + 1

    if not event_import_index:
        event_import_index = Event.select(fn.Max(Event.import_index)).scalar()

    corrections = Event.select().where(
        Event.import_index == event_import_index,
        Event.label == "Picked a correction",
    )
    for correction in corrections:
        correction_data = json.loads(correction.data)
        if correction_data['type'] in DEFINITION_CORRECTION_TYPES:
            DefinitionCorrection.create(
                compute_index=compute_index,
                participant_id=correction.participant_id,
                correction_type=correction_data['type'],
                symbol_name=correction_data['suggestion']['symbol']['name'],
                time=correction.time,
            )


def configure_parser(parser):
    parser.description = "Extract list of corrections to missing definitions"
    parser.add_argument(
        "--event-import-index",
        type=int,
        help="Version of imported events from which to extract choices."
    )
