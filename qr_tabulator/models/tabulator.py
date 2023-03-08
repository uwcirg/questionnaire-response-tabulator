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
import json
from fhir.resources.bundle import Bundle
from fhir.resources.questionnaireresponse import QuestionnaireResponse
from fhir.resources.resource import Resource

def write_table(df:pd.DataFrame, location=None, type='csv'):
    if location is None:
        location = Path.cwd()
    else:
        location = Path(location).absolute()
        location.mkdir(parents=True, exist_ok=True)
    datetime = time.strftime("%Y-%m-%d-%H%M%S")
    basename = f"QuestionnaireResponse-{datetime}"
    if type == 'csv':
        ext = 'csv'
        write_fn = lambda dataframe, path: dataframe.to_csv(path, index=False)
    path = location / f"{basename}.{ext}"
    write_fn(df, path)
    return path


def preprocess_qr(entries):
    # Denormalize QR entries on items
    new_entries = []
    for entry in entries:
        resource = entry['resource']
        for item in resource['item']:
            entry_template = copy.deepcopy(entry)
            entry_template['resource']['item'] = [ copy.deepcopy(item) ]
            # Replace resource id with has to avoid collisions in tabulator
            entry_template['resource']['id_original'] = entry_template['resource']['id']
            entry_template['resource']['id'] = hash(json.dumps(entry_template, default=str, ensure_ascii=True, sort_keys=True))
            new_entries.append(entry_template)
    print(len(entries))
    print(len(new_entries))
    return new_entries


def get_bundle_entries_of_type(bundle_dict, resource_type:Resource):
    valid_bundle = Bundle.parse_obj(bundle_dict)
    bundle_dict_entries = bundle_dict['entry']
    filtered_entries = []
    for idx, entry in enumerate(valid_bundle.entry):
        if isinstance(entry.resource, resource_type):
           filtered_entries.append(bundle_dict_entries[idx])
    return filtered_entries


def tabulate_qr(bundle):
    schema_path = Path(__file__).parent/"DefaultQuestionnaireResponseSchema.yaml" # Path to a schema config file.
    schema = load_schema(schema_path)
    entries = get_bundle_entries_of_type(bundle, QuestionnaireResponse)
    preprocessed_data = preprocess_qr(entries)
    tabulated_results = tabulate_data(preprocessed_data, schema, "QuestionnaireResponse")
    df = pd.DataFrame(columns=tabulated_results[0], data=tabulated_results[1:])
    return df