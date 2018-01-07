from peewee import fn
import json

from models import Event, LineChoice


def main(event_import_index=None, vcode_event_import_index, *args, **kwargs):

    last_compute_index = LineChoice.select(
        fn.Max(LineChoice.compute_index)).scalar() or 0
    compute_index = last_compute_index + 1

    if not event_import_index:
        event_import_index = Event.select(fn.Max(Event.import_index)).scalar()
    if not vcode_event_import_index:
        vcode_event_import_index = VcodeEvent.select(fn.Max(VcodeEvent.import_index)).scalar()

    line_choices = Event.select().where(
        Event.import_index == event_import_index,
        Event.label == "Clicked on line number",
    )
    for choice in line_choices:
        choice_data = json.loads(choice.data)
        LineChoice.create(
            compute_index=compute_index,
            participant_id=choice.participant_id,
            time=choice.time,
            line_number=choice_data['lineNumber'],
        )

    vcode_line_choices = VcodeEvent.select().where(
        VcodeEvent.import_index == vcode_event_import_index,
        VcodeEvent.label == "Add line",
    )
    for choice in vcode_line_choices:



def configure_parser(parser):
    parser.description = "Extract all choices of lines to include in the example"
    parser.add_argument(
        "--event-import-index",
        type=int,
        help="Version of imported events from which to extract choices."
    )
    parser.add_argument(
        "--vcode-event-import-index",
        type=int,
        help="Version of imported VCode events from which to extract choices."
    )
