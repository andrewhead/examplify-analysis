import logging
import json
import os
import re
from peewee import fn

from models import VcodeEvent


def _decode_data_field(field):
    return field.replace("&#44;", ",")


def main(log_directory, *args, **kwargs):

    last_import_index = VcodeEvent.select(
        fn.Max(VcodeEvent.import_index)).scalar() or 0
    import_index = last_import_index + 1

    # Load in a list of all events from a global activity log.
    for log_filename in os.listdir(log_directory):

        with open(os.path.join(log_directory, log_filename), encoding='iso-8859-1') as log:

            # Get the participant ID from the log name
            participant_id = int(re.match(
                r"participant(\d+)-evts.txt", log_filename).group(1))

            # Start at line 5; those before are headers and whitespace
            for line in log.readlines()[4:]:

                print(line)

                # Unpack data for this event into fields
                fields = line.strip().split(',')
                start_ms = int(fields[0])
                length_ms = int(fields[1])
                event_type = _decode_data_field(fields[2])
                event_data = _decode_data_field(fields[3])
                if event_data == "(null)":
                    event_data = None

                # Save the event to the database
                VcodeEvent.create(
                    import_index=import_index,
                    participant_id=participant_id,
                    start_ms=start_ms,
                    length_ms=length_ms,
                    label=event_type,
                    data=event_data,
                )


def configure_parser(parser):
    parser.description = "Import interaction events from a log."
    parser.add_argument(
        "log_directory",
        help=(
            "Directory containing a list of data files produced by VCode.  Each of " +
            "these files should have a name like participant#-evts.txt"
        )
    )
