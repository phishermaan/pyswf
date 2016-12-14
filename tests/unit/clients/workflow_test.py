# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import mock
import pytest

from datetime import datetime

from py_swf.clients.workflow import _build_time_filter_dict
from py_swf.clients.workflow import WorkflowClient


@pytest.fixture
def workflow_config():
    return mock.Mock()


@pytest.fixture
def workflow_client(workflow_config, boto_client):
    return WorkflowClient(workflow_config, boto_client)


@pytest.fixture
def oldest_start_date():
    return datetime(2016, 11, 11)


@pytest.fixture
def latest_start_date():
    return datetime(2016, 11, 12)


@pytest.fixture
def oldest_close_date():
    return datetime(2016, 11, 28)


@pytest.fixture
def latest_close_date():
    return datetime(2016, 11, 29)


def test_start_workflow(workflow_config, workflow_client, boto_client):
    boto_return = mock.MagicMock()
    boto_client.start_workflow_execution.return_value = boto_return
    actual_run_id = workflow_client.start_workflow(
        input='meow',
        id='cat',
    )

    boto_client.start_workflow_execution.assert_called_once_with(
        domain=workflow_config.domain,
        childPolicy='TERMINATE',
        workflowId='cat',
        input='meow',
        workflowType={
            'name': workflow_config.workflow_name,
            'version': workflow_config.workflow_version,
        },
        taskList={
            'name': workflow_config.task_list,
        },
        executionStartToCloseTimeout=str(workflow_config.execution_start_to_close_timeout),
        taskStartToCloseTimeout=str(workflow_config.task_start_to_close_timeout),
    )
    assert actual_run_id == boto_return['runId']


def test_terminate_workflow(workflow_config, workflow_client, boto_client):
    workflow_client.terminate_workflow(
        'workflow_id',
        'reason',
    )
    boto_client.terminate_workflow_execution.assert_called_once_with(
        domain=workflow_config.domain,
        workflowId='workflow_id',
        reason='reason',
    )


def test_build_time_filter_dict_without_date():
    time_filter_dict = _build_time_filter_dict()
    assert time_filter_dict == {}


def test_build_time_filter_dict_with_oldest_start_date(oldest_start_date):
    time_filter_dict = _build_time_filter_dict(oldest_start_date=oldest_start_date)
    assert 'startTimeFilter' in time_filter_dict
    assert time_filter_dict['startTimeFilter'] == {'oldestDate': oldest_start_date}


def test_build_time_filter_dict_with_oldest_close_date(oldest_close_date):
    time_filter_dict = _build_time_filter_dict(oldest_close_date=oldest_close_date)
    assert 'closeTimeFilter' in time_filter_dict
    assert time_filter_dict['closeTimeFilter'] == {'oldestDate': oldest_close_date}


def test_build_time_filter_dict_with_start_date_range(oldest_start_date, latest_start_date):
    time_filter_dict = _build_time_filter_dict(oldest_start_date=oldest_start_date, latest_start_date=latest_start_date)
    assert 'startTimeFilter' in time_filter_dict
    assert time_filter_dict['startTimeFilter'] == {'oldestDate': oldest_start_date, 'latestDate': latest_start_date}


def test_build_time_filter_dict_with_close_date_range(oldest_close_date, latest_close_date):
    time_filter_dict = _build_time_filter_dict(oldest_close_date=oldest_close_date, latest_close_date=latest_close_date)
    assert 'closeTimeFilter' in time_filter_dict
    assert time_filter_dict['closeTimeFilter'] == {'oldestDate': oldest_close_date, 'latestDate': latest_close_date}


def test_count_open_workflow_executions_with_oldest_start_time(workflow_config, workflow_client, boto_client, oldest_start_date):
    workflow_client.count_open_workflow_executions(
        oldest_start_date=oldest_start_date,
    )
    boto_client.count_open_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
    )


def test_count_open_workflow_executions_with_start_time_range(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
        latest_start_date
):
    workflow_client.count_open_workflow_executions(
        oldest_start_date=oldest_start_date,
        latest_start_date=latest_start_date,
    )
    boto_client.count_open_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(
            oldestDate=oldest_start_date,
            latestDate=latest_start_date,
        ),
    )


def test_count_open_workflow_executions_with_oldest_start_time_and_workflow_name(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_open_workflow_executions(
        oldest_start_date=oldest_start_date,
        workflow_name='test',
        version='test',
    )
    boto_client.count_open_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        typeFilter=dict(
            name='test',
            version='test',
        )
    )


def test_count_open_workflow_executions_with_oldest_start_time_and_tag(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_open_workflow_executions(
        oldest_start_date=oldest_start_date,
        tag='test',
    )
    boto_client.count_open_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        tagFilter=dict(tag='test'),
    )


def test_count_open_workflow_executions_with_oldest_start_time_and_workflow_id(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_open_workflow_executions(
        oldest_start_date=oldest_start_date,
        workflow_id='test'
    )
    boto_client.count_open_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        executionFilter=dict(workflowId='test'),
    )


def test_count_closed_workflow_executions_and_oldest_start_time(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_closed_workflow_executions(oldest_start_date=oldest_start_date)
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date)
    )


def test_count_closed_workflow_executions_with_start_time_range(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
        latest_start_date,
):
    workflow_client.count_closed_workflow_executions(oldest_start_date=oldest_start_date, latest_start_date=latest_start_date)
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(
            oldestDate=oldest_start_date,
            latestDate=latest_start_date,
        )
    )


def test_count_closed_workflow_executions_with_oldest_close_time(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_close_date,
):
    workflow_client.count_closed_workflow_executions(oldest_close_date=oldest_close_date)
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        closeTimeFilter=dict(oldestDate=oldest_close_date),
    )


def test_count_closed_workflow_executions_with_close_time_range(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_close_date,
        latest_close_date,
):
    workflow_client.count_closed_workflow_executions(oldest_close_date=oldest_close_date, latest_close_date=latest_close_date)
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        closeTimeFilter=dict(oldestDate=oldest_close_date, latestDate=latest_close_date),
    )


def test_count_closed_workflow_executions_with_oldest_start_time_and_workflow_name(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_start_date=oldest_start_date,
        workflow_name='test',
        version='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        typeFilter=dict(
            name='test',
            version='test',
        ),
    )


def test_count_closed_workflow_executions_with_oldest_close_time_and_workflow_name(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_close_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_close_date=oldest_close_date,
        workflow_name='test',
        version='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        closeTimeFilter=dict(oldestDate=oldest_close_date),
        typeFilter=dict(
            name='test',
            version='test',
        ),
    )


def test_count_closed_workflow_executions_with_oldest_start_time_and_tag(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_start_date=oldest_start_date,
        tag='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        tagFilter=dict(tag='test'),
    )


def test_count_closed_workflow_executions_with_oldest_close_time_and_tag(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_close_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_close_date=oldest_close_date,
        tag='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        closeTimeFilter=dict(oldestDate=oldest_close_date),
        tagFilter=dict(tag='test'),
    )


def test_count_closed_workflow_executions_with_oldest_start_time_and_workflow_id(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_start_date=oldest_start_date,
        workflow_id='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        executionFilter=dict(workflowId='test'),
    )


def test_count_closed_workflow_executions_with_oldest_close_time_and_workflow_id(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_close_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_close_date=oldest_close_date,
        workflow_id='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        closeTimeFilter=dict(oldestDate=oldest_close_date),
        executionFilter=dict(workflowId='test'),
    )


def test_count_closed_workflow_executions_with_oldest_start_time_and_close_status(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_start_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_start_date=oldest_start_date,
        close_status='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        startTimeFilter=dict(oldestDate=oldest_start_date),
        closeStatusFilter=dict(status='test'),
    )


def test_count_closed_workflow_executions_with_oldest_close_time_and_close_status(
        workflow_config,
        workflow_client,
        boto_client,
        oldest_close_date,
):
    workflow_client.count_closed_workflow_executions(
        oldest_close_date=oldest_close_date,
        close_status='test',
    )
    boto_client.count_closed_workflow_executions.assert_called_with(
        domain=workflow_config.domain,
        closeTimeFilter=dict(oldestDate=oldest_close_date),
        closeStatusFilter=dict(status='test'),
    )
