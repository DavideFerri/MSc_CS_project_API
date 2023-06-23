from pydantic import BaseSettings


class Settings(BaseSettings):
    check_expiration = True
    jwt_header_prefix = "Bearer"
    jwt_header_name = "Authorization"
    userpools = {
        "eu": {
            "region": "eu-north-1",
            "userpool_id": "eu-north-1_X3JgREkfA",
            "app_client_id": ["78ub9qdd3232mogmobphft7b75"] # Example with multiple ids
        }
    }
    aws_cognito_app_client_id = "78ub9qdd3232mogmobphft7b75"



