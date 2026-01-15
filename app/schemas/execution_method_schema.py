from pydantic import BaseModel

class Genrocket_mirror_payload(BaseModel):
    username: str
    password: str
    clientAppId: str
    clientUserId: str
    scenario: str
    scenarioPath: str
    keepFileName: bool