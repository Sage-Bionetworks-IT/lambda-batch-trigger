import os

import boto3
import pytest

from botocore.stub import Stubber
from submit_job import app


@pytest.fixture
def batch_client():
    """
    This creates a single client used by all tests
    """
    return boto3.client('batch')


@pytest.fixture
def mock_submit_response():
    """
    Mock response from 'submit_job'
    """
    return {
        'jobId': 'test-id',
        'jobName': 'test-name',
    }


def test_handler(mocker, batch_client, mock_submit_response):
    """
    Happy-path test, ensure HTTP 200
    """
    env_vars = {
        'JOB_NAME': 'test-name',
        'JOB_QUEUE': 'test-queue',
        'JOB_DEFINITION': 'test-definition',
    }
    mocker.patch.dict(os.environ, env_vars)

    mocker.patch('submit_job.app.get_batch_client', return_value=batch_client)

    with Stubber(batch_client) as stubber:
        stubber.add_response('submit_job', mock_submit_response)

        response = app.lambda_handler({}, {})  # neither argument is used
        assert response['statusCode'] == 200
        stubber.assert_no_pending_responses()


def test_client_error(mocker, batch_client):
    """
    Ensure we get HTTP 400 on a ClientError
    """

    # If these are unset, boto will raise ParamValidationError, not ClientError
    env_vars = {
        'JOB_NAME': 'test-name',
        'JOB_QUEUE': 'test-queue',
        'JOB_DEFINITION': 'test-definition',
    }
    mocker.patch.dict(os.environ, env_vars)

    mocker.patch('submit_job.app.get_batch_client', return_value=batch_client)

    with Stubber(batch_client) as stubber:
        stubber.add_client_error('submit_job')

        response = app.lambda_handler({}, {})  # neither argument is used
        assert response['statusCode'] == 400
        stubber.assert_no_pending_responses()
