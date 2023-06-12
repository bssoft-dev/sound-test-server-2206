from typing import Any, Generic

from fastapi import Response

from fastapi_users import models
from fastapi_users.authentication.strategy import (
    Strategy,
    StrategyDestroyNotSupportedError,
)
from fastapi_users.authentication.transport import (
    Transport,
    TransportLogoutNotSupportedError,
)
from fastapi_users.types import DependencyCallable


class AuthenticationBackend(Generic[models.UC, models.UD]):
    """
    Combination of an authentication transport and strategy.

    Together, they provide a full authentication method logic.

    :param name: Name of the backend.
    :param transport: Authentication transport instance.
    :param get_strategy: Dependency callable returning
    an authentication strategy instance.
    """

    name: str
    transport: Transport

    def __init__(
        self,
        name: str,
        transport: Transport,
        get_strategy: DependencyCallable[Strategy[models.UC, models.UD]],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy

    async def login(
        self,
        strategy: Strategy[models.UC, models.UD],
        user: models.UD,
        response: Response,
    ) -> Any:
        token = await strategy.write_token(user)
        #Modified for Emergency Bell Dashboard Development
        # if 'customerCode' in user.__dict__:
        #     return await self.transport.get_login_response(token, response, user.customerCode, f'http://api-2207.bs-soft.co.kr/api/images/{user.customerCode}.png', user.is_hyperuser)
        # else:
        #     return await self.transport.get_login_response(token, response)
        return await self.transport.get_login_response(token, response, f'http://api-2207.bs-soft.co.kr/api/images/{user.username}.png', user.is_hyperuser)

    async def logout(
        self,
        strategy: Strategy[models.UC, models.UD],
        user: models.UD,
        token: str,
        response: Response,
    ) -> Any:
        try:
            await strategy.destroy_token(token, user)
        except StrategyDestroyNotSupportedError:
            pass
        try:
            await self.transport.get_logout_response(response)
        except TransportLogoutNotSupportedError:
            return None
