"""FileObject module."""

from __future__ import annotations

import dataclasses

from mlcroissant._src.core import constants
from mlcroissant._src.core.context import Context
from mlcroissant._src.core.data_types import check_expected_type
from mlcroissant._src.core.json_ld import box_singleton_list
from mlcroissant._src.core.json_ld import remove_empty_values
from mlcroissant._src.core.json_ld import unbox_singleton_list
from mlcroissant._src.core.types import Json
from mlcroissant._src.core.uuid import generate_uuid
from mlcroissant._src.core.uuid import uuid_from_jsonld
from mlcroissant._src.core.uuid import uuid_to_jsonld
from mlcroissant._src.structure_graph.base_node import Node
from mlcroissant._src.structure_graph.nodes.source import Source


@dataclasses.dataclass(eq=False, repr=False)
class FileObject(Node):
    """Nodes to describe a dataset FileObject (distribution)."""

    uuid: dataclasses.InitVar[str]
    content_url: str | None = None
    content_size: str | None = None
    contained_in: list[str] | None = None
    description: str | None = None
    encoding_format: str | None = None
    md5: str | None = None
    name: str = ""
    same_as: list[str] | None = None
    sha256: str | None = None
    source: Source | None = None

    def __post_init__(self, uuid: str | None = None):
        """Checks arguments of the node and sets UUID."""
        if not uuid:
            uuid = generate_uuid()
        self._uuid = uuid
        self.validate_name()
        self.assert_has_mandatory_properties("encoding_format", "name", "_uuid")
        if not self.contained_in:
            self.assert_has_mandatory_properties("content_url")
            if self.ctx and not self.ctx.is_live_dataset:
                self.assert_has_exclusive_properties(["md5", "sha256"])

    def to_json(self) -> Json:
        """Converts the `FileObject` to JSON."""

        if isinstance(self.contained_in, list) and len(self.contained_in) == 1:
            contained_in: str | list[str] | dict = self.contained_in[0]
        else:
            contained_in = self.contained_in
        if not self.ctx.is_v0():
            if isinstance(contained_in, list):
                contained_in = [{"@id": uuid_to_jsonld(source)} for source in contained_in]  # type: ignore
            elif isinstance(contained_in, str):
                contained_in = {"@id": uuid_to_jsonld(contained_in)}

        return remove_empty_values({
            "@type": "sc:FileObject" if self.ctx.is_v0() else "cr:FileObject",
            "@id": uuid_to_jsonld(self.uuid),  # pytype: disable=wrong-arg-types
            "name": self.name,
            "description": self.description,
            "contentSize": self.content_size,
            "contentUrl": self.content_url,
            "containedIn": unbox_singleton_list(self.contained_in),
            "encodingFormat": self.encoding_format,
            "md5": self.md5,
            "sameAs": unbox_singleton_list(self.same_as),
            "sha256": self.sha256,
            "source": self.source.to_json() if self.source else None,
        })

    @classmethod
    def from_jsonld(
        cls,
        ctx: Context,
        file_object: Json,
    ) -> FileObject:
        """Creates a `FileObject` from JSON-LD."""
        check_expected_type(
            ctx.issues, file_object, constants.SCHEMA_ORG_FILE_OBJECT(ctx)
        )
        content_url = file_object.get(constants.SCHEMA_ORG_CONTENT_URL)
        name = file_object.get(constants.SCHEMA_ORG_NAME, "")

        if contained_in is not None and not isinstance(contained_in, list):
            contained_in = [contained_in]
        if contained_in is not None and not ctx.is_v0():
            contained_in = [uuid_from_jsonld(source) for source in contained_in]

        content_size = file_object.get(constants.SCHEMA_ORG_CONTENT_SIZE)
        description = file_object.get(constants.SCHEMA_ORG_DESCRIPTION)
        encoding_format = file_object.get(constants.SCHEMA_ORG_ENCODING_FORMAT)
        return cls(
            ctx=ctx,
            content_url=content_url,
            content_size=content_size,
            contained_in=box_singleton_list(
                file_object.get(constants.SCHEMA_ORG_CONTAINED_IN)
            ),
            description=description,
            encoding_format=encoding_format,
            md5=file_object.get(constants.SCHEMA_ORG_MD5(ctx)),
            name=name,
            same_as=box_singleton_list(file_object.get(constants.SCHEMA_ORG_SAME_AS)),
            sha256=file_object.get(constants.SCHEMA_ORG_SHA256),
            source=file_object.get(constants.ML_COMMONS_SOURCE(ctx)),
            uuid=uuid_from_jsonld(file_object),
        )
