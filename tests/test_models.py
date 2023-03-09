import json
import shutil
from pathlib import Path
from pytest import fixture
from qr_tabulator.models.tabulator import (
    tabulate_qr,
    get_bundle_entries_of_type,
    preprocess_qr,
    write_table,
)
from fhir.resources.questionnaireresponse import QuestionnaireResponse
import pandas as pd


class MockResponse(object):
    """Wrap data in response like object"""

    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code == 200:
            return
        raise Exception("status code ain't 200")


def load_jsondata(datadir, filename):
    with open(Path.joinpath(datadir, filename), "r") as jsonfile:
        data = json.load(jsonfile)
    return data


@fixture
def qnr_response_example(datadir):
    return load_jsondata(datadir, "QnrResponseExample.json")


@fixture
def qnr_response_example_mixed(datadir):
    return load_jsondata(datadir, "QnrResponseExampleMixed.json")


@fixture
def qnr_response_example_simple(datadir):
    return load_jsondata(datadir, "QnrResponseExampleSimple.json")


@fixture
def qnr_response_example_entry_list(datadir):
    return load_jsondata(datadir, "QnrResponseExampleEntryList.json")


def test_get_bundle_entries_of_type_simple(qnr_response_example_simple):
    type = QuestionnaireResponse
    entries = get_bundle_entries_of_type(qnr_response_example_simple, type)
    assert len(entries) == 1
    resource = type.parse_obj(entries[0]["resource"])
    assert isinstance(resource, type)


def test_get_bundle_entries_of_type_mixed(qnr_response_example_mixed):
    type = QuestionnaireResponse
    entries = get_bundle_entries_of_type(qnr_response_example_mixed, type)
    assert len(entries) == 1
    resource = type.parse_obj(entries[0]["resource"])
    assert isinstance(resource, type)


def test_qr_preprocessing(qnr_response_example_entry_list):
    entry_list = qnr_response_example_entry_list
    processed_entries = preprocess_qr(qnr_response_example_entry_list)
    assert len(processed_entries) == len(entry_list[0]["resource"]["item"])
    for entry in processed_entries:
        assert len(entry["resource"]["item"]) == 1


def test_write_table_no_location():
    df = pd.DataFrame()
    path = write_table(df)
    assert path.exists()
    assert path.parent == Path.cwd()
    path.unlink()


def test_write_table_location():
    df = pd.DataFrame()
    folder = Path("test_output")
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    path = write_table(df, folder)
    assert path.exists()
    assert path.parent == Path.cwd() / folder
    path.unlink()
    shutil.rmtree(folder, ignore_errors=True)


def test_tabulate_qr(qnr_response_example):
    table = tabulate_qr(qnr_response_example)
    assert isinstance(table, pd.DataFrame)
    assert len(table.index) == 79
