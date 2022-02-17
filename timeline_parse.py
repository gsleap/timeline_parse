from datetime import datetime, timedelta
import json
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

def getPlaceLocation(key, value):
    if value == "HOME":
        location = "Assuming home"
    else:
        startTimestamp = iso_timestamp_to_datetime(
            value["duration"]["startTimestamp"])
        endTimestamp = iso_timestamp_to_datetime(
            value["duration"]["endTimestamp"])

        d_hours, d_mins, d_secs = time_difference_in_h_m_s(
        startTimestamp, endTimestamp)

        location = value["location"]["address"].replace("\n", " ").replace(",", " ")
    return location


def parse_google_timeline_json(filename: str, output_file_handle):
    print(f"Parsing {filename}...")

    with open(filename) as json_file:
        # returns JSON object as
        # a dictionary
        # The google "Takeout" JSON file consists of items which are activitySegments (think: travel) or placeVisits (you can figure that one out!)
        data = json.load(json_file)
        print(f"{filename} read and parsed successfully.")

        timeline_list = list(data["timelineObjects"])
        item_count = len(timeline_list)

        for i in range(0, item_count - 1):
            # There is no record before the first one
            if i == 0:
                prev_key = "placeVisit"
                prev_value = "HOME"
            else:
                prev_key = list(timeline_list[i-1])[0]
                prev_value = list(timeline_list[i-1].values())[0]
                            
            key0 = list(timeline_list[i])[0]
            value0 = list(timeline_list[i].values())[0]

            next_key = list(timeline_list[i+1])[0]
            next_value = list(timeline_list[i+1].values())[0]
                    
            if key0 == "activitySegment":
                startTimestamp = iso_timestamp_to_datetime(
                    value0["duration"]["startTimestamp"])
                endTimestamp = iso_timestamp_to_datetime(
                    value0["duration"]["endTimestamp"])

                activityType = value0["activityType"]
                distance_m = value0["distance"]
                d_hours, d_mins, d_secs = time_difference_in_h_m_s(
                    startTimestamp, endTimestamp)

                if activityType == "IN_PASSENGER_VEHICLE" and prev_key == "placeVisit" and next_key == "placeVisit":
                    prev_location = getPlaceLocation(prev_key, prev_value)
                    next_location = getPlaceLocation(next_key, next_value)
                       
                    output_file_handle.write(f'"{prev_location}","{next_location}",{startTimestamp:%d/%m/%Y %H:%M:%S},{endTimestamp:%d/%m/%Y %H:%M:%S},{distance_m/1000.}\n')
                    print(
                            f"{activityType} from: {prev_location} to {next_location} at time {startTimestamp} to {endTimestamp} ({d_hours}h {d_mins}m {d_secs}s) {distance_m} m")

            elif key0 == "placeVisit":
                pass
                
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

        # open csv for output
        output_filename = "output.csv"
        with open(output_filename, "w") as output_file_handle:
            # ok, let's do the parsing
            parse_google_timeline_json(filename, output_file_handle)

        print(f"CSV written to {output_filename}. I'm done!")
    else:
        print("Usage: \npython timeline_parse.py GOOGLE_JSON_FILENAME\n")
        exit(1)
