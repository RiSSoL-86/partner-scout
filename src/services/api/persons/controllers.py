from http import HTTPStatus
from typing import final

from dmr import Controller, Path, Query, ResponseSpec, modify
from dmr.errors import ErrorModel
from dmr.plugins.pydantic import PydanticSerializer

from services.api.persons.exceptions import PersonNotFoundError
from services.api.persons.path_params import PersonPathParams
from services.api.persons.schemas import (
    PageQuery,
    PersonChoicesResponse,
    PersonListQuery,
    PersonListResponse,
    PersonResponse,
    PersonSourcesResponse,
)
from services.api.persons.services.list import PersonListService
from services.api.persons.services.sources import PersonSourcesService


@final
class PersonChoicesController(Controller[PydanticSerializer]):
    """Return selectable choice values for person mentions."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Persons"])
    async def get(self) -> PersonChoicesResponse:
        """Return the person mention choice values with labels."""
        return PersonChoicesResponse.build()


@final
class PersonListController(Controller[PydanticSerializer]):
    """List persons with optional name filtering."""

    auth = None

    @modify(status_code=HTTPStatus.OK, tags=["Persons"])
    async def get(
        self,
        parsed_query: Query[PersonListQuery],
    ) -> PersonListResponse:
        """Return a page of persons filtered by name."""
        service = PersonListService()
        persons, total = await service.execute(
            search=parsed_query.search,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )
        return PersonListResponse(
            items=[PersonResponse.build(person) for person in persons],
            total=total,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )


@final
class PersonSourcesController(Controller[PydanticSerializer]):
    """List every source known for one person across all scans."""

    auth = None

    @modify(
        status_code=HTTPStatus.OK,
        tags=["Persons"],
        extra_responses=[
            ResponseSpec(ErrorModel, status_code=HTTPStatus.NOT_FOUND),
        ],
    )
    async def get(
        self,
        parsed_path: Path[PersonPathParams],
        parsed_query: Query[PageQuery],
    ) -> PersonSourcesResponse:
        """Return a page of the person's sources or a 404 error."""
        service = PersonSourcesService()
        result = await service.execute(
            person_id=parsed_path.person_id,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )
        if result is None:
            raise PersonNotFoundError

        person, sources, total = result
        return PersonSourcesResponse.build(
            person=person,
            sources=sources,
            total=total,
            offset=parsed_query.offset,
            limit=parsed_query.limit,
        )
