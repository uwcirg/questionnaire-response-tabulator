"""
Tabulate QuestionnaireResponse data
    Only for QuestionnaireResponses
    Start with TrueNth fields, use as default
    Once that's working, add:
        Accept field map (fields, path, order)
        Option to sort on a set of fields
"""
from pathlib import Path
from phdi.tabulation import load_schema
from phdi.fhir.tabulation import tabulate_data
import pandas as pd
import copy
import time

REPORT_TYPE = "QuestionnaireResponse"

def write(df:pd.DataFrame, location=None, type='csv'):
    if location is None:
        location = Path.cwd()
    else:
        location = Path(location)
        if not location.exists():
            location.mkdir(parents=True)
    datetime = time.strftime("%Y-%m-%d-%H%M%S")
    basename = f"{REPORT_TYPE}-{datetime}"
    path = location/f"{basename}.{type}"
    if type == 'csv':
        df.to_csv(path, index=False)
    return path

def preprocess(entries):
    # Denormalize QR entries on items
    new_entries = []
    for entry in entries:
        resource = entry['resource']
        for item in resource['item']:
            entry_template = copy.deepcopy(entry)
            entry_template['resource']['item'] = [ item ]
            new_entries.append(entry_template)
    return new_entries

def tabulate_qr(data):
    schema = load_schema(Path(f"DefaultSchema.yaml"))  # Path to a schema config file.
    if isinstance(data, dict) and 'entry' in data.keys():
        entries = data['entry']
    else:
        raise ValueError("Input must be a FHIR Bundle")
    preprocessed_data = preprocess(entries)
    tabulated_results = tabulate_data(preprocessed_data, schema, REPORT_TYPE)
    df = pd.DataFrame(data=tabulated_results[1:], columns=tabulated_results[0])
    return df