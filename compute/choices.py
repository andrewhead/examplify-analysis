from peewee import fn
import json

from models import Event, Choice


def main(event_import_index=None, *args, **kwargs):

    last_compute_index = Choice.select(fn.Max(Choice.compute_index)).scalar() or 0
    compute_index = last_compute_index + 1

    if not event_import_index:
        event_import_index = Event.select(fn.Max(Event.import_index)).scalar()

    choices = Event.select().where(
        Event.import_index == event_import_index,
        Event.label << ["Accepted extension", "Rejected extension"]
    )
    for choice in choices:
        event_data = json.loads(choice.data)
        Choice.create(
            compute_index=compute_index,
            participant_id=choice.participant_id,
            accepted=(choice.label == "Accepted extension"),
            time=choice.time,
            extension_type=event_data['type'],
        )


def configure_parser(parser):
    parser.description = "Extract list of choices about inclusions"
    parser.add_argument(
        "--event-import-index",
        type=int,
        help="Version of imported events from which to extract choices."
    )
