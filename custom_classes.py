from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from authentication import get_client_id_from_token
from authorization import user_access_authorization

class CustomRequest(Request):
    def __init__(self):
        self.logged_in_user_id: int


class APIRouteWrapper(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: CustomRequest) -> Response:
            if self.path not in ['/client/updatedata/login']:
                logged_in_user_id = await get_client_id_from_token(request)
                request.logged_in_user_id = logged_in_user_id
                user_access_authorization(req_method=request.method, req_path=self.path, user_id=logged_in_user_id)
            return await original_route_handler(request=request)
        return custom_route_handler
