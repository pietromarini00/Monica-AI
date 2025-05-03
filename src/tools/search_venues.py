
from src.tools.base_tool import BaseTool

tool_config = {
    "type": "function",
    "function": {
        "name": "search_venues",
        "description": "Search for venues in a given area. ",
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
            "required": ["venue_type", "location"],
        },
    }
}

class SearchVenuesTool(BaseTool):
    def __init__(self, name: str, config: dict = tool_config):
        super().__init__(name, config)

    def run(self, **kwargs) -> str:
        print(kwargs)


if __name__ == "__main__":
    tool = SearchVenuesTool("search_venues")
    print(tool.run(venue_type="restaurant", location="New York"))
