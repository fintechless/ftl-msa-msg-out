"""
Tests for MSA MSG OUT, part of the PLATFORM category
"""


import json
import uuid
from typing import Any, Dict

from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from ftl_python_lib.models.transaction import ModelTransaction
from ftl_python_lib.typings.models.transaction import TypeTransaction

MSA_OUT_URL: str = "/msa/out"


# pylint: disable=R0903
class TestMsaMsgOut:
    """
    Test class for testing MSA MSG OUT
    """

    @staticmethod
    def test_msa_msg_out_post(
        flask_test_client_msa_msg_out: FlaskClient,
        transaction_test_model: ModelTransaction,
        valid_xml: str,
    ) -> None:
        """
        Test the POST /msa/out endpoint with valid XML message
        Should return 200 status code
        """

        transaction: TypeTransaction = transaction_test_model.initiate()
        response: TestResponse = flask_test_client_msa_msg_out.post(
            MSA_OUT_URL,
            headers={
                "X-Transaction-Id": transaction.transaction_id,
                "Content-Type": "application/xml",
            },
            data=valid_xml,
        )

        data: Dict[str, Any] = json.loads(response.data)

        assert response.status_code == 200
        assert data.get("status") == "OK"
        assert data.get("message") == "Request was received"
        assert data.get("request_id") == str(
            uuid.UUID(hex=data.get("request_id"), version=4)
        )
    
    @staticmethod
    def test_msa_msg_out_missing_xml_post(
        flask_test_client_msa_msg_out: FlaskClient,
        transaction_test_model: ModelTransaction,
    ) -> None:
        """
        Test the POST /msa/out endpoint with missing XML message
        Should return 400 status code
        """

        transaction: TypeTransaction = transaction_test_model.initiate()
        response: TestResponse = flask_test_client_msa_msg_out.post(
            MSA_OUT_URL,
            headers={
                "X-Transaction-Id": transaction.transaction_id,
                "Content-Type": "application/xml",
            },
        )

        data: Dict[str, Any] = json.loads(response.data)

        assert response.status_code == 400
        assert data.get("status") == "Rejected"
        assert data.get("message") == "Missing message body"
        assert data.get("request_id") == str(
            uuid.UUID(hex=data.get("request_id"), version=4)
        )
    
    @staticmethod
    def test_msa_msg_in_missing_headers_post(
        flask_test_client_msa_msg_out: FlaskClient,
        valid_xml: str,
    ) -> None:
        """
        Test the POST /msa/in endpoint with missing transaction id header
        Should return 400 status code
        """

        response: TestResponse = flask_test_client_msa_msg_out.post(
            MSA_OUT_URL,
            headers={
                "Content-Type": "application/xml",
            },
            data=valid_xml,
        )

        data: Dict[str, Any] = json.loads(response.data)

        assert response.status_code == 400
        assert data.get("status") == "Rejected"
        assert data.get("message") == "Missing X-Transaction-Id HTTP header"
        assert data.get("request_id") == str(
            uuid.UUID(hex=data.get("request_id"), version=4)
        )
    
    @staticmethod
    def test_msa_msg_out_not_initiated_transaction_post(
        flask_test_client_msa_msg_out: FlaskClient,
        valid_xml: str,
    ) -> None:
        """
        Test the POST /msa/out endpoint with a transaction that was not initiated
        Should return 400 status code
        """

        response: TestResponse = flask_test_client_msa_msg_out.post(
            MSA_OUT_URL,
            headers={
                "X-Transaction-Id": str(uuid.uuid4()),
                "Content-Type": "application/xml",
            },
            data=valid_xml,
        )

        data: Dict[str, Any] = json.loads(response.data)

        assert response.status_code == 404
        assert data.get("status") == "Rejected"
        assert data.get("message") == "Could not find such transaction"
        assert data.get("request_id") == str(
            uuid.UUID(hex=data.get("request_id"), version=4)
        )
    
    @staticmethod
    def test_msa_msg_out_trailing_slash_post(
        flask_test_client_msa_msg_out: FlaskClient,
    ) -> None:
        """
        Test the POST /msa/in/ endpoint
        Should return 404 status code
        """

        response: TestResponse = flask_test_client_msa_msg_out.post(f"{MSA_OUT_URL}/")

        assert response.status_code == 404

    @staticmethod
    def test_msa_msg_out_healthy_get(flask_test_client_msa_msg_out: FlaskClient) -> None:
        """
        Test the GET /msa/in/_healthy endpoint
        Should return valid UUIDs and a healthy status
        """

        response: TestResponse = flask_test_client_msa_msg_out.get(f"{MSA_OUT_URL}/_healthy")

        data: Dict[str, Any] = json.loads(response.data)

        assert response.status_code == 200
        assert data.get("status") == "OK"
        assert data.get("request_id") == str(
            uuid.UUID(hex=data.get("request_id"), version=4)
        )

    @staticmethod
    def test_msa_msg_out_healthy_trailing_slash_get(
        flask_test_client_msa_msg_out: FlaskClient,
    ) -> None:
        """
        Test the GET /msa/in/_healthy/ endpoint
        Should return 404 status code
        """

        response: TestResponse = flask_test_client_msa_msg_out.get(f"{MSA_OUT_URL}/_healthy/")

        assert response.status_code == 404
