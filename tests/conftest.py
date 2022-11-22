import pytest
import pathlib
import pickle
import shioaji as sj


def read_contracts_pkl():
    data_path = pathlib.Path(__file__).parent.absolute()
    with open(f"{data_path}/data/contracts.pkl", "rb") as f:
        contracts = pickle.load(f)
    return contracts


@pytest.fixture
def sj_api():
    api = sj.Shioaji()
    api.Contracts = read_contracts_pkl()
    return api


