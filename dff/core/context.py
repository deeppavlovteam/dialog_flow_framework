import logging
from uuid import UUID, uuid4

from typing import ForwardRef
from typing import Any, Optional, Union

from pydantic import BaseModel, validate_arguments, Field, validator
from .types import NodeLabel2Type


logger = logging.getLogger(__name__)

Context = ForwardRef("Context")


@validate_arguments
def sort_dict_keys(dictionary: dict) -> dict:
    return {key: dictionary[key] for key in sorted(dictionary)}


@validate_arguments
def get_last_index(dictionary: dict) -> int:
    indexes = list(dictionary)
    return indexes[-1] if indexes else 0


class Context(BaseModel):
    id: Union[UUID, int, str] = Field(default_factory=uuid4)
    node_labels: dict[int, NodeLabel2Type] = {}
    requests: dict[int, Any] = {}
    responses: dict[int, Any] = {}
    misc: dict[str, Any] = {}
    validation: bool = False

    # validators
    _sort_node_labels = validator("node_labels", allow_reuse=True)(sort_dict_keys)
    _sort_requests = validator("requests", allow_reuse=True)(sort_dict_keys)
    _sort_responses = validator("responses", allow_reuse=True)(sort_dict_keys)

    @classmethod
    def cast(
        cls,
        ctx: Union[Context, dict, str] = {},
        *args,
        **kwargs,
    ) -> Union[Context, dict, str]:
        if not ctx:
            ctx = Context()
        elif isinstance(ctx, dict):
            ctx = Context.parse_obj(ctx)
        elif isinstance(ctx, str):
            ctx = Context.parse_raw(ctx)
        elif not issubclass(type(ctx), Context):
            raise ValueError(
                f"context expected as sub class of Context class or object of dict/str(json) type, but got {ctx}"
            )
        return ctx

    @validate_arguments
    def add_request(self, request: Any):
        last_index = get_last_index(self.requests)
        self.requests[last_index + 1] = request

    @validate_arguments
    def add_response(self, response: Any):
        last_index = get_last_index(self.responses)
        self.responses[last_index + 1] = response

    @validate_arguments
    def add_node_label(self, node_label: NodeLabel2Type):
        last_index = get_last_index(self.node_labels)
        self.node_labels[last_index + 1] = node_label

    @validate_arguments
    def clear(self, hold_last_n_indexes: int, field_names: list[str] = ["requests", "responses", "node_labels"]):
        if "requests" in field_names:
            for index in list(self.requests)[:-hold_last_n_indexes]:
                del self.requests[index]
        if "responses" in field_names:
            for index in list(self.responses)[:-hold_last_n_indexes]:
                del self.responses[index]
        if "mics" in field_names:
            self.misc.clear()
        if "node_labels" in field_names:
            for index in list(self.node_labels)[:-hold_last_n_indexes]:
                del self.node_labels[index]

    @property
    def last_node_label(self) -> Optional[NodeLabel2Type]:
        last_index = get_last_index(self.node_labels)
        return self.node_labels.get(last_index)

    @property
    def last_response(self) -> Optional[Any]:
        last_index = get_last_index(self.responses)
        return self.responses.get(last_index)

    @property
    def last_request(self) -> Optional[Any]:
        last_index = get_last_index(self.requests)
        return self.requests.get(last_index)


Context.update_forward_refs()
