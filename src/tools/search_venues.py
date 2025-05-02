
from src.tools.base_tool import BaseTool

tool_config = {
    "type": "function",
    "function": {
        "name": "search_venues",
        "description": (
            "Search for venues in a given area. "
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "venue_type": {
                    "type": "string",
                    "description": "The type of venue to search for.",
                },
                "location": {
                    "type": "string",
                    "description": "The location to search for venues.",
                },
            },
            "required": ["symbol"],
        },
    }
}

class SearchVenuesTool(BaseTool):

    def __init__(self, name: str, config: dict = tool_config):
        super().__init__(name, config)

    def run(self, **kwargs) -> str:
        pass
