"""FileSet module."""

from __future__ import annotations

import dataclasses

from rdflib.namespace import SDO

from mlcroissant._src.core import constants
from mlcroissant._src.core.context import Context
from mlcroissant._src.core.dataclasses import jsonld_field
from mlcroissant._src.core.dataclasses import JsonldField
from mlcroissant._src.core.uuid import formatted_uuid_to_json
from mlcroissant._src.core.uuid import uuid_from_jsonld
from mlcroissant._src.structure_graph.base_node import NodeV2

OriginalField = dataclasses.Field
dataclasses.Field = JsonldField  # type: ignore


@dataclasses.dataclass(eq=False, repr=False)
class FileSet(NodeV2):
    """Nodes to describe a dataset FileSet (distribution)."""

    contained_in: list[str] | None = jsonld_field(
        cardinality="MANY",
        default_factory=list,
        description=(
            "Another FileObject or FileSet that this one is contained in, e.g., in the"
            " case of a file extracted from an archive. When this property is present,"
            " the contentUrl is evaluated as a relative path within the container"
            " object"
        ),
        from_jsonld=lambda ctx, contained_in: uuid_from_jsonld(contained_in),
        input_types=[SDO.Text],
        to_jsonld=lambda ctx, contained_in: [
            formatted_uuid_to_json(ctx, uuid) for uuid in contained_in
        ],
        url=SDO.containedIn,
    )
    description: str | None = jsonld_field(
        default=None,
        input_types=[SDO.Text],
        url=SDO.description,
    )
    encoding_format: str | None = jsonld_field(
        default=None,
        description="The format of the file, given as a mime type.",
        input_types=[SDO.Text],
        required=True,
        url=SDO.encodingFormat,
    )
    excludes: list[str] | None = jsonld_field(
        cardinality="MANY",
        default=None,
        description="A glob pattern that specifies the files to exclude.",
        input_types=[SDO.Text],
        url=lambda ctx: constants.ML_COMMONS_EXCLUDES(ctx),
    )
    includes: list[str] | None = jsonld_field(
        cardinality="MANY",
        default=None,
        description="A glob pattern that specifies the files to include.",
        input_types=[SDO.Text],
        url=lambda ctx: constants.ML_COMMONS_INCLUDES(ctx),
    )
    name: str = jsonld_field(
        default="",
        description=(
            "The name of the file.  As much as possible, the name should reflect the"
            " name of the file as downloaded, including the file extension. e.g."
            ' "images.zip".'
        ),
        input_types=[SDO.Text],
        url=SDO.name,
    )

    def __post_init__(self):
        """Checks arguments of the node."""
        self.validate_name()
        self.assert_has_mandatory_properties(
            "includes", "encoding_format", "name", "id"
        )

    @classmethod
    def _JSONLD_TYPE(cls, ctx: Context):
        """Gets the class' JSON-LD @type."""
        return constants.SCHEMA_ORG_FILE_SET(ctx)


dataclasses.Field = OriginalField  # type: ignore
