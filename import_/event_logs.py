import logging
import json
import os
from peewee import fn
from dateutil.parser import parse as parse_timestamp

from models import Event


def main(log_filename, bounds_json, *args, **kwargs):

    last_import_index = Event.select(fn.Max(Event.import_index)).scalar() or 0
    import_index = last_import_index + 1

    # Load in a list of all events from a global activity log.
    events = []
    with open(log_filename) as log:
        for line in log:
            event = json.loads(line.strip())
            # Replace the timestamp with a datetime object
            event['time'] = parse_timestamp(event['timestamp'])
            events.append(event)

    task_bounds = []
    with open(bounds_json) as bounds_file:
        task_bounds = json.load(bounds_file)
        for bounds in task_bounds:
            # Replace the timestamps for bounds with datetime objects
            bounds['start_time'] = parse_timestamp(bounds['start_time'])
            bounds['end_time'] = parse_timestamp(bounds['end_time'])


    for bounds in task_bounds:

        # Collect all events that occurred within the time bound
        for event in events:
            if (event['time'] >= bounds['start_time'] and
                    event['time'] <= bounds['end_time']):
                Event.create(
                    import_index=import_index,
                    participant_id=bounds['participant_id'],
                    tool=bounds['tool_name'],
                    time=event['time'],
                    label=event['label'],
                    data=json.dumps(event['data']) if 'data' in event else "{}",
                )


def configure_parser(parser):
    parser.description = "Import interaction events from a log."
    parser.add_argument(
        "log_filename",
        help=(
            "Log file containing interaction events.  Each line is a distinct event " +
            "formatted as a JSON object with a label, timestamp, and data field."
        )
    )
    parser.add_argument(
        "bounds_json",
        help=(
            "A JSON file, with a list of records.  Each record has a " +
            "participant_id, tool_name, start_time, and end_time.  start_time and end_time " +
            "are Unix timestamps."
        )
    )
