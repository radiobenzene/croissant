"""Tests for RecordSets."""

from unittest import mock

import pytest

from mlcroissant._src.core import constants
from mlcroissant._src.core.context import Context
from mlcroissant._src.core.context import CroissantVersion
from mlcroissant._src.structure_graph.base_node import Node
from mlcroissant._src.structure_graph.nodes.field import Field
from mlcroissant._src.structure_graph.nodes.record_set import get_parent_uuid
from mlcroissant._src.structure_graph.nodes.record_set import RecordSet
from mlcroissant._src.tests.nodes import create_test_field
from mlcroissant._src.tests.nodes import create_test_node
from mlcroissant._src.tests.nodes import create_test_record_set
from mlcroissant._src.tests.versions import parametrize_conforms_to


@pytest.mark.parametrize(
    ["data", "error"],
    [
        [
            {"foo": "bar"},
            (
                "[RecordSet(record_set_name)] http://mlcommons.org/croissant/data"
                " should declare a list. Got: <class 'dict'>."
            ),
        ],
        [
            [],
            (
                "[RecordSet(record_set_name)] http://mlcommons.org/croissant/data"
                " should declare a non empty list."
            ),
        ],
        [
            [[{"foo": "bar"}]],
            (
                "[RecordSet(record_set_name)] http://mlcommons.org/croissant/data"
                " should declare a list of dict. Got: a list of <class 'list'>."
            ),
        ],
        [
            [{"foo": "bar"}],
            (
                "[RecordSet(record_set_name)] Line #0 doesn't have the expected"
                " columns. Expected: {'field_name'}. Got: {'foo'}."
            ),
        ],
    ],
)
def test_invalid_data(data, error):
    ctx = Context()
    field = create_test_field(ctx=ctx)
    create_test_record_set(
        ctx=ctx,
        data=data,
        fields=[field],
    )
    assert error in ctx.issues.errors


def test_checks_are_performed():
    with mock.patch.object(
        Node, "assert_has_mandatory_properties"
    ) as mandatory_mock, mock.patch.object(
        Node, "assert_has_optional_properties"
    ) as optional_mock, mock.patch.object(
        Node, "validate_name"
    ) as validate_name_mock:
        create_test_node(RecordSet)
        mandatory_mock.assert_called_once_with("name", "id")
        optional_mock.assert_called_once_with("description")
        validate_name_mock.assert_called_once()


@parametrize_conforms_to()
def test_from_jsonld(conforms_to: CroissantVersion):
    ctx = Context(conforms_to=conforms_to)
    jsonld = {
        "@type": constants.ML_COMMONS_RECORD_SET_TYPE(ctx),
        "@id": "foo_id",
        constants.SCHEMA_ORG_NAME: "foo",
        constants.SCHEMA_ORG_DESCRIPTION: "bar",
        constants.ML_COMMONS_IS_ENUMERATION(ctx): True,
        constants.SCHEMA_ORG_KEY(ctx): ["key1", "key2"],
        constants.ML_COMMONS_DATA(ctx): [{"column1": ["value1", "value2"]}],
    }
    record_set = RecordSet.from_jsonld(ctx, jsonld)
    assert record_set.name == "foo"
    assert record_set.description == "bar"
    assert record_set.is_enumeration == True
    assert record_set.key == ["key1", "key2"]
    assert record_set.data == [{"column1": ["value1", "value2"]}]
    assert ctx.issues.errors == {
        (
            "[RecordSet(foo)] Line #0 doesn't have the expected columns. Expected:"
            " set(). Got: {'column1'}."
        ),
        (
            "[RecordSet(foo)] Line #0 doesn't have the expected columns. Expected:"
            " set(). Got: {'column1'}."
        ),
    }


@pytest.mark.parametrize(
    ["node_type", "uuid", "parent_uuid", "input", "output"],
    [
        [RecordSet, "foo", "other", "foo", "foo"],
        [Field, "foo/bar", "foo", "bar", "foo"],
    ],
)
def test_get_parent_uuid(node_type, uuid, parent_uuid, input, output):
    mocked_node = mock.Mock(uuid=uuid, spec_set=node_type)
    mocked_node.parent.uuid = parent_uuid
    mocked_ctx = Context()
    mocked_ctx.node_by_uuid = mock.Mock(return_value=mocked_node)
    assert get_parent_uuid(mocked_ctx, input) == output
