"""
Flask view for the MSG OUT blueprint
Path: /
"""

import threading

from flask import Response
from flask import make_response
from flask import request
from flask import session
from ftl_python_lib.constants.messages import ConstantsMessagesAllowRelease
from ftl_python_lib.constants.models.mapping import ConstantsMappingSourceType
from ftl_python_lib.core.context.environment import EnvironmentContext
from ftl_python_lib.core.context.request import REQUEST_CONTEXT_SESSION
from ftl_python_lib.core.context.request import RequestContext
from ftl_python_lib.core.exceptions.client_invalid_request_exception import ExceptionInvalidRequest
from ftl_python_lib.core.exceptions.server_unexpected_error_exception import ExceptionUnexpectedError
from ftl_python_lib.core.log import LOGGER
from ftl_python_lib.core.microservices.api.mapping import MicroserviceApiMapping
from ftl_python_lib.core.microservices.api.mapping import MircoserviceApiMappingResponse
from ftl_python_lib.core.microservices.which import which_microservice_am_i
# from ftl_python_lib.models.liquidity import ModelLiquidity
from ftl_python_lib.models.transaction import ModelTransaction
from ftl_python_lib.typings.iso20022.received_message import TypeReceivedMessage
from ftl_python_lib.typings.iso20022.received_message import TypeReceivedMessageOut
from ftl_python_lib.utils.mime import mime_is_json
from ftl_python_lib.utils.mime import mime_is_xml
from ftl_python_lib.utils.xml.to_pacs_002 import pacs_008_to_pacs_002

from ftl_msa_msg_out.msa.blueprints import BLUEPRINT_MSG_OUT


def threaded(**kwargs) -> None:
    LOGGER.logger.debug("Running threaded process for MSA MSG PACS 008 microservice")
    request_context: RequestContext = kwargs.get("request_context")
    environ_context: EnvironmentContext = kwargs.get("environ_context")
    # pacs.008 message
    incoming: TypeReceivedMessage = kwargs.get("incoming")

    # Required models and providers
    transaction_model: ModelTransaction = ModelTransaction(
        request_context=request_context, environ_context=environ_context
    )
    # liquidity_model: ModelLiquidity = ModelLiquidity(
    #     request_context=request_context, environ_context=environ_context
    # )
    mapping: MicroserviceApiMapping = MicroserviceApiMapping(
        request_context=request_context, environ_context=environ_context
    )

    try:
        incoming.upload_to_storage(incoming=False)

        mapping_response: MircoserviceApiMappingResponse = mapping.get(
            params={
                "source_type": ConstantsMappingSourceType.SOURCE_TYPE_MESSAGE_OUT.value,
                "source": ConstantsMappingSourceType.SOURCE_MESSAGE_OUT.value,
                "content_type": incoming.content_type,
                "message_type": incoming.message_type,
            }
        )
        for mapping_item in mapping_response.data:
            target: str = mapping_item.target

            LOGGER.logger.debug(f"Sending new request to target '{target}'")

            microservice_instance = which_microservice_am_i(name=target)(
                request_context=request_context, environ_context=environ_context
            )

            if mime_is_xml(mime=incoming.content_type):
                LOGGER.logger.debug(f"Sending new request to target as XML")
                microservice_instance.post(
                    data=incoming.message_xml,
                    headers=request_context.headers_context.request_headers,
                )
            if mime_is_json(mime=incoming.content_type):
                LOGGER.logger.debug(f"Sending new request to target as JSON")
                microservice_instance.post(
                    data=incoming.message_proc,
                    headers=request_context.headers_context.request_headers,
                )

        # if "pacs.008" in message_custom.message_type and "pacs-008" not in request.headers.get("X-Transaction-Target"):
        #     liquidity_model.liquidity(
        #         deployment_id=request_context.deployment_id,
        #         entity_id=message_custom.creditor_name,
        #         user_id=message_custom.creditor_account,
        #         currency=message_custom.currency,
        #         amount=-message_custom.amount,
        #     )
        if incoming.message_type in ConstantsMessagesAllowRelease:
            transaction_model.release(
                storage_path=incoming.storage_path.key,
                message_type=incoming.message_version,
                ht_response_code="ACSC",
                ht_response_message="ACSC",
                currency=incoming.message_proc.currency,
                amount=incoming.message_proc.amount
            )
        LOGGER.logger.debug("Finshed threaded process for MSA MSG OUT microservice")
    except Exception as err:
        LOGGER.logger.error(err)

        mapping_response: MircoserviceApiMappingResponse = mapping.get(
            params={
                "source_type": ConstantsMappingSourceType.SOURCE_TYPE_MESSAGE_OUT.value,
                "source": ConstantsMappingSourceType.SOURCE_MESSAGE_OUT.value,
                "content_type": incoming.content_type,
                "message_type": incoming.message_type_out_failed,
            }
        )
        for mapping_item in mapping_response.data:
            target: str = mapping_item.target

            LOGGER.logger.debug(f"Sending new request to target '{target}'")

            microservice_instance = which_microservice_am_i(name=target)(
                request_context=request_context, environ_context=environ_context
            )

            if mime_is_xml(mime=incoming.content_type):
                LOGGER.logger.debug(f"Sending new request to target as XML")
                microservice_instance.post(
                    data=incoming.message_xml,
                    headers=request_context.headers_context.request_headers,
                )
            if mime_is_json(mime=incoming.content_type):
                LOGGER.logger.debug(f"Sending new request to target as JSON")
                microservice_instance.post(
                    data=incoming.message_proc,
                    headers=request_context.headers_context.request_headers,
                )

        transaction_model.fail()

        raise ExceptionUnexpectedError(
            message=f"Unexpected server error: {str(err)}",
            request_context=request_context,
        ) from err


# pylint: disable=R0915
# too-many-statements
@BLUEPRINT_MSG_OUT.route("", methods=["POST"])
def post() -> Response:
    """
    Process POST request for the /msa/out endpoint
    Send new transaction
    """

    request_context: RequestContext = session.get(REQUEST_CONTEXT_SESSION)
    environ_context: EnvironmentContext = EnvironmentContext()

    if len(request.data) == 0 or request.data is None:
        LOGGER.logger.error("Missing message body")
        raise ExceptionInvalidRequest(
            message="Missing message body", request_context=request_context
        )
    if (
        request_context.transaction_id is None
        or request_context.headers_context.transaction_id is None
    ):
        LOGGER.logger.error("Missing X-Transaction-Id HTTP header")
        raise ExceptionInvalidRequest(
            message="Missing X-Transaction-Id HTTP header",
            request_context=request_context,
        )

    LOGGER.logger.debug(
        "\n".join(
            [
                "Proccessing POST request for MSG OUT microservice",
                f"Request ID is {request_context.request_id}",
                f"Transaction ID is {request_context.transaction_id}",
                f"Request timestamp is {request_context.requested_at_datetime}",
            ]
        )
    )

    incoming: TypeReceivedMessage = TypeReceivedMessage(
        request_context=request_context,
        environ_context=environ_context,
        message_raw=request.data,
        content_type=request_context.headers_context.content_type,
    )

    try:
        incoming.fill_message_xml()
        incoming.fill_message_proc()
        incoming.fill_message_type()
        incoming.fill_message_version(from_header=incoming.fill_message_version(from_header=request_context.headers_context.message_type))
        incoming.fill_message_version_keys()
    except ValueError as exception:
        LOGGER.logger.error(exception)
        raise ExceptionInvalidRequest(
            message="Received an invalid incoming message",
            request_context=request_context,
        ) from exception

    threading.Thread(
        target=threaded,
        kwargs={
            "request_context": request_context,
            "environ_context": environ_context,
            "incoming": incoming,
        },
    ).start()

    return make_response(
        {
            "request_id": request_context.request_id,
            "status": "OK",
            "message": "Request was received",
        },
        201,
    )
