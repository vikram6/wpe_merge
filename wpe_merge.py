import urllib.request
import argparse
import logging
import json
import csv
import sys
import os

logger = logging.getLogger(__name__)


class CSV:
    @staticmethod
    def read_csv_file(input_file):
        data = []
        with open(input_file) as csvfile:
            read_csv = csv.DictReader(csvfile)
            for row in read_csv:
                data.append(row)

        return data

    @staticmethod
    def write_csv_file(output_file, data):
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['Account ID', 'First Name', 'Created On', 'Status', 'Status Set On'])

            writer.writeheader()
            for row in data:
                writer.writerow(row)

def make_request(account_id):
    try:
        logger.debug("Querying for account id '%s'" % (account_id))
        resp = urllib.request.urlopen("http://interview.wpengine.io/v1/accounts/" + account_id)
    except Exception as e:
        logger.error("Unable to get data for account id '%s'. Error returned was '%s'" % (account_id, e))
        return {}

    return json.loads(resp.read())

def get_data_from_api(data):
    output_data = []
    for row in data:
        if not row.get("Account ID"):
            logger.warning("%s doesn't have a valid 'Account ID'. Skipping it." % (row))
            continue

        logger.info("Processing account id %s" % (row["Account ID"]))
        result = make_request(row["Account ID"])
        if result:
            new_row = {
                "Account ID": row["Account ID"],
                "First Name": row.get("First Name"),
                "Created On": row.get("Created On"),
                "Status": result.get("status"),
                "Status Set On": result.get("created_on")
            }
            output_data.append(new_row)

    return output_data

def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", metavar="INPUT_CSV")
    parser.add_argument("output", metavar="OUTPUT_CSV")

    args = parser.parse_args()
    return args

def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_command_line()
    input_file, output_file = args.input, args.output

    if not os.path.exists(input_file):
        logger.error("The given input does not exist: '%s'" % (input_file))
        sys.exit(1)

    csv_helper = CSV()
    data = csv_helper.read_csv_file(input_file)

    output_data = get_data_from_api(data)

    csv_helper.write_csv_file(output_file, output_data)

if __name__ == "__main__":
    main()
