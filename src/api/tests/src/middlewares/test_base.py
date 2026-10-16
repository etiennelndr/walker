from functools import wraps

from quart import Quart

from walker.api import middlewares
from walker.api.middlewares import Middleware
from walker.api.typing import Route


async def test_middleware_order(app: Quart) -> None:
    middleware_entries = []

    def middleware(name: str) -> Middleware:
        def _decorator[**P](route: Route[P, str]) -> Route[P, str]:
            @wraps(route)
            async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
                if name.startswith("req"):
                    middleware_entries.append(name)
                    args += (name,)
                result = await route(*args, **kwargs)
                if name.startswith("res"):
                    middleware_entries.append(name)
                return result

            return _wrapper

        return _decorator

    @app.get("/test")
    @middlewares.request(
        middleware("req1"),
        middleware("req2"),
    )
    @middlewares.response(
        middleware("res1"),
        middleware("res2"),
    )
    async def test(*values: str):
        return ".".join(values)

    assert middleware_entries == []

    async with app.test_client() as test_client:
        await test_client.get("/test")

    assert middleware_entries == [
        "req1",
        "req2",
        "res1",
        "res2",
    ]
