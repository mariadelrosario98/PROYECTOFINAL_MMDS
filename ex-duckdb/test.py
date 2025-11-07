# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "boto3",
#     "pytest",
# ]
# ///


import boto3
import pytest

import main

def test(source: str):

    # test when there are no files in the bucket
    assert main.main(source) == {
        "rate_2xx": 0.5,
        "rate_4xx": 0.2,
        "rate_5xx": 0.3,
    }

@pytest.fixture()
def soruce() -> str:
    # TODO: use boto3 to create test data in the bucket
    # and verify that the outputs are correct.
    yield "s3://test-bucket"

    # TODO: delete the test data
