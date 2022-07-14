"""
Pytest configuration file
Used for defining fixtures
"""

import os
from unittest import mock
from typing import Generator

from flask.testing import FlaskClient
import pytest
from ftl_python_lib.core.context.environment import EnvironmentContext
from ftl_python_lib.core.context.request import RequestContext
from ftl_python_lib.models.transaction import ModelTransaction
import ftl_msa_msg_out.msa.run


@pytest.fixture(autouse=True)
def mock_base_environ() -> Generator:
    """
    Add relevant environment variables
    """

    environ: dict = {
        "AWS_ACCESS_KEY_ID": "dummyaccess",
        "AWS_SECRET_ACCESS_KEY": "dummysecret",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_ACCOUNT_ID": "123456789012",
        "KAFKA_BROKER": "localhost:9092",
        "KAFKA_MESSAGE_INBOX_TARGET": "topic-msg-in-pacs-008",
        "KAFKA_MESSAGE_OUTBOX_TARGET": "topic-msg-out-pacs-008",
        "FTL_ENVIRONMENT": "default",
        "FTL_PASSIVE_REGION": "us-east-1",
        "FTL_CLOUD_PROVIDER_API_ENDPOINT_URL": "http://localhost:4566",
        "FTL_MSA_UUID_TTL": "5",
        "FTL_RUNTIME_BUCKET": "ftl-api-runtime-default-us-east-1-123456789012",
    }

    with mock.patch.dict(os.environ, environ):
        yield


@pytest.fixture
def flask_test_client_msa_msg_out() -> FlaskClient:
    """
    Create test client of the FLASK application for MSA MSG OUT
    """

    app = ftl_msa_msg_out.msa.run.create_app()
    app.app_context().push()

    return app.test_client()


@pytest.fixture
def transaction_test_model() -> ModelTransaction:
    """
    Create test model for Transaction
    """

    request_context: RequestContext = RequestContext()
    return ModelTransaction(
        request_context=RequestContext(),
        environ_context=EnvironmentContext(request_context=request_context),
    )


@pytest.fixture
def valid_xml() -> str:
    """
    Valid XML message
    """

    with open("tests/static/valid.xml", encoding="utf-8") as fin:
        return fin.read()


@pytest.fixture
def invalid_xml() -> str:
    """
    Invalid XML message
    """

    with open("tests/static/invalid.xml", encoding="utf-8") as fin:
        return fin.read()
