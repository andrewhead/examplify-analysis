from peewee import fn
import json
from datetime import datetime, timedelta

from models import Event, Choice, VcodeEvent


def main(event_import_index, vcode_event_import_index, *args, **kwargs):

    last_compute_index = Choice.select(fn.Max(Choice.compute_index)).scalar() or 0
    compute_index = last_compute_index + 1

    if not event_import_index:
        event_import_index = Event.select(fn.Max(Event.import_index)).scalar()

    if not vcode_event_import_index:
        vcode_event_import_index = VcodeEvent.select(fn.Max(VcodeEvent.import_index)).scalar()

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

    vcode_choices = VcodeEvent.select(
            VcodeEvent.participant_id,
            VcodeEvent.start_ms,
            # Group events by their start time, as the only way for
            # us to catch some extension choices is by considering
            # pairs of labels (or lack of pairs) for replies.
            fn.group_concat(VcodeEvent.label, "|").alias('labels')
        ).where(
            VcodeEvent.import_index == vcode_event_import_index,
            VcodeEvent.label << [
                "Ã Throw Exception",
                "x Throw Exception",
                "Ã Control",
                "x Control",
                "Reply to sugg.",
            ]
        ).group_by(VcodeEvent.participant_id, VcodeEvent.start_ms)

    for choice in vcode_choices:

        # Convert the event metadata from the Vcode logs into the
        # data format produced from the original CodeScoop logs.
        if choice.labels == "Reply to sugg.":
            accepted = False
            extension_type = "MediatingUseExtension"
        elif "Throw Exception" in choice.labels:
            accepted = "Ã" in choice.labels
            extension_type = "MethodThrowsExtension"
        elif "Control" in choice.labels:
            accepted = "Ã" in choice.labels
            extension_type = "ControlStructureExtension"

        # For conformance to the other records, we synthesize a datetime for
        # each event from Vcode.  The first event is always at the UNIX
        # start time.  Even though these times are obviously wrong, the
        # time between events for each participant is still correct.
        fake_time = datetime(2017, 1, 1, 0, 0, 0) +\
            timedelta(milliseconds=choice.start_ms)

        # Create the record of the choice
        Choice.create(
            compute_index=compute_index,
            participant_id=choice.participant_id,
            accepted=accepted,
            time=fake_time,
            extension_type=extension_type,
        )


def configure_parser(parser):
    parser.description = "Extract list of choices about inclusions"
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
