import requests
import json
import argparse
import os
def parse_args():
    # setup arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--scoring_uri", type=str, default = None)
    parser.add_argument("--scoring_key",type=str, default = None)
    # parse args
    args = parser.parse_args()

    # return args
    return args



def main(args):
    # Convert to a serializable list in a JSON document
    x_new= {'vendorID': {715: '2', 3633: '2'},
    'lpepPickupDatetime': {715: '2016-01-04 20:48:38',3633: '2016-02-15 20:35:58'},
    'passengerCount': {715: '1', 3633: '1'},
    'tripDistance': {715: '1.14', 3633: '6.43'},
    'pickupLongitude': {715: '-73.97727966308594', 3633: '-73.95679473876953'},
    'pickupLatitude': {715: '40.68115234375', 3633: '40.74812316894531'},
    'dropoffLongitude': {715: '-73.96723175048828', 3633: '-73.9059066772461'},
    'dropoffLatitude': {715: '40.67363739013672', 3633: '40.76784896850586'},
    'month_num': {715: '1', 3633: '2'},
    'day_of_month': {715: '4', 3633: '15'},
    'day_of_week': {715: '0', 3633: '0'},
    'hour_of_day': {715: '20', 3633: '20'},
    'country_code': {715: 'US', 3633: 'US'},
    'hr_sin': {715: '-0.866025403784439', 3633: '-0.866025403784439'},
    'hr_cos': {715: '0.4999999999999992', 3633: '0.4999999999999992'},
    'dy_sin': {715: '0.0', 3633: '0.0'},
    'dy_cos': {715: '1.0', 3633: '1.0'},
    'datetime': {715: '2016-01-04 00:00:00', 3633: '2016-02-15 00:00:00'},
    'normalizeHolidayName': {715: 'nan', 3633: "Washington's Birthday"},
    'isPaidTimeOff': {715: 'nan', 3633: 'True'},
    'precipTime': {715: '1.0', 3633: '24.0'},
    'temperature': {715: '0.12389380530973423', 3633: '-6.222602739726026'},
    'precipDepth': {715: '0.0', 3633: '9999.0'}}
    input_json = json.dumps({"data": x_new})

    # Call the web service, passing the input data (the web service will also accept the data in binary format)
    scoring_key= args.scoring_key
    scoring_uri = args.scoring_uri
    if not scoring_key:
        scoring_key = os.environ.get("SCORING_KEY")
    if not scoring_uri:
        scoring_uri = os.environ.get("SCORING_URI")
    

    # Set the content type
    headers = { 'Content-Type':'application/json', 'Authorization':('Bearer '+ scoring_key)}

    predictions = requests.post(scoring_uri, input_json, headers = headers)
    print ("Result:", json.loads(predictions.json()))

    #return json.dumps(predictions.tolist())


# run script
if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main function
    main(args)