from datetime import datetime, timedelta
import json
from locale import D_FMT
import os
import sys
import time


def iso_timestamp_to_datetime(iso_timestamp_string: str) -> datetime:
    # The format from google may or may not have microseconds so check both
    try:
        return_date = datetime.strptime(
            iso_timestamp_string, "%Y-%m-%dT%H:%M:%S.%f%z")
    except:
        return_date = datetime.strptime(
            iso_timestamp_string, "%Y-%m-%dT%H:%M:%S%z")

    # Determine the offset from UTC that the current timezone
    date_now = time.time()
    offset = datetime.fromtimestamp(
        date_now) - datetime.utcfromtimestamp(date_now)

    return return_date + offset


def time_difference_in_h_m_s(startTimestamp: datetime, endTimestamp: datetime):
    duration_secs = float((
        endTimestamp - startTimestamp).total_seconds())
    d_hours = int(duration_secs / 3600.)
    d_mins = int((duration_secs - (d_hours * 3600.)) / 60.)
    d_secs = int(duration_secs -
                 (d_hours * 3600.) - (d_mins * 60.))

    return d_hours, d_mins, d_secs


def parse_google_timeline_json(filename: str):
    print(f"Parsing {filename}...")

    with open(filename) as json_file:
        # returns JSON object as
        # a dictionary
        # The google "Takeout" JSON file consists of items which are activitySegments (think: travel) or placeVisits (you can figure that one out!)
        data = json.load(json_file)
        print(f"{filename} read and parsed successfully.")

        prev_line_output = False

        for level0 in data["timelineObjects"]:
            for key0, value0 in level0.items():
                if key0 == "activitySegment":
                    startTimestamp = iso_timestamp_to_datetime(
                        value0["duration"]["startTimestamp"])
                    endTimestamp = iso_timestamp_to_datetime(
                        value0["duration"]["endTimestamp"])

                    activityType = value0["activityType"]
                    distance_m = value0["distance"]
                    d_hours, d_mins, d_secs = time_difference_in_h_m_s(
                        startTimestamp, endTimestamp)

                    # add some criteria here!
                    # e.g. only passenger vehicles on the 4th Feb 2022
                    if activityType == "IN_PASSENGER_VEHICLE" and startTimestamp.year == 2022 and startTimestamp.month == 2 and startTimestamp.day == 4:
                        print(
                            f"Activity Smegment: {activityType} from: {startTimestamp} to {endTimestamp} ({d_hours}h {d_mins}m {d_secs}s) {distance_m} m")
                        prev_line_output = True
                    else:
                        prev_line_output = False

                elif key0 == "placeVisit":
                    startTimestamp = iso_timestamp_to_datetime(
                        value0["duration"]["startTimestamp"])
                    endTimestamp = iso_timestamp_to_datetime(
                        value0["duration"]["endTimestamp"])

                    d_hours, d_mins, d_secs = time_difference_in_h_m_s(
                        startTimestamp, endTimestamp)

                    location = value0["location"]["address"].replace("\n", " ")

                    # only show a place if we previously showed an activitySegment
                    if prev_line_output:
                        print(
                            f"Place Visit: {location} from: {startTimestamp} to {endTimestamp} ({d_hours}h {d_mins}m {d_secs}s)")
                else:
                    print("No idea how to process {key0}")
                    exit(3)


if __name__ == "__main__":
    # Get command line args
    if len(sys.argv) == 2:
        filename = sys.argv[1]

        # Does the file exist?
        if not os.path.exists(filename):
            print(f"Error: {filename} does not exist!")
            exit(2)

        # ok, let's do the parsing
        parse_google_timeline_json(filename)
    else:
        print("Usage: \npython timeline_parse.py GOOGLE_JSON_FILENAME\n")
        exit(1)
