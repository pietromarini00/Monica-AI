import os
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler
from src.ui import OnboardingForm
from src.tools.messanger import WeddingWireRequest, tool_config
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")

from data.venues import venues

venues_string = [str(venue) for venue in venues]

class Chat:
    def __init__(self, onboarding_info: OnboardingForm):
        self.client = OpenAI(api_key=OPEN_API_KEY)
        # define the assistant
        self.assistant = self.client.beta.assistants.create(
            name="Wedding Planner",
            instructions="""
            You are an expert wedding concierge and planner.

You will receive a one-sentence description of a couple's dream wedding. Your task is to curate three unique and compelling vendor combinations that each include:

One venue

One flower vendor

One catering vendor

One DJ or entertainment vendor

All vendors must be selected only from the provided dataset. For each combination, explain how the vendors come together to fulfill the couple's vision. Your explanation should be emotionally resonant, vivid, and persuasive—like a wedding planner pitching their dream day.

Tone: Romantic, confident, aspirational. Think lifestyle magazine meets luxury planner.

Guidelines:

Do not invent vendor names or capabilities—only use information from the dataset.

Match by theme, price point, vibe, and geography where possible.

For each vendor, consider their services, reviews, pricing, and city.

Avoid repeating the same vendor across all 3 options.

The explanation should reflect how this combo suits the couple's desires and elevate their dream—through setting, food, flowers, and entertainment.

Input Example:
"A sophisticated garden wedding with elegant touches, local cuisine, and live entertainment for 80 guests."

Output Format:

Option 1:
🏛️ Venue: [Venue Name]
💐 Flowers: [Flower Vendor Name]
🍽️ Catering: [Caterer Name]
🎧 DJ: [DJ or Entertainment Vendor Name]
Why this works: [A 3–5 sentence explanation selling the vision.]

Option 2:
...

Option 3:
...
""",
            tools=[tool_config],
            model="gpt-4o-mini"
        )

        self.thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=f"User onboarding info: {str(onboarding_info.model_dump())} \n\n Venues: {venues_string}",
        )


    async def run(self, user_message: str) -> str | tuple[str, dict]:
        logger.info(f"Starting run with message: {user_message[:100]}...")
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message,
        )
        # model response
        event_handler = EventHandler()
        logger.info("Starting assistant stream")
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
        logger.info("Assistant stream completed")

        # Execute any tool calls
        logger.info("Executing tool calls")
        tool_result = await event_handler.execute_tool_calls()
        logger.info("Tool execution completed")

        # Return just the response if no tool calls were made
        if not event_handler.tool_calls:
            logger.info("No tool calls made, returning just the response")
            return event_handler.get_full_response(), None

        logger.info("Tool calls were made, returning response and tool result")
        return event_handler.get_full_response(), tool_result

    def test(self):
        onboarding = OnboardingForm(
            name="Alex",
            partner_name="Jamie",
            wedding_date="2025-10-12",
            budget=25000,
            location="Napa Valley"
        )

        self.run(onboarding)


class EventHandler(AssistantEventHandler):
    def __init__(self):
        super().__init__()
        self.full_response = ""
        self.tool_calls = []
        logger.info("EventHandler initialized")

    def on_text_delta(self, delta, snapshot):
        self.full_response += delta.value
        logger.debug(f"Received text delta: {delta.value}")

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'function':
            if delta.function.name:
                logger.info(f"Received tool call: {delta.function.name}")
                logger.debug(f"Tool call arguments: {delta.function.arguments}")
                self.tool_calls.append({
                    'name': delta.function.name,
                    'arguments': delta.function.arguments
                })

    def on_error(self, error):
        logger.error(f"Error in EventHandler: {error}")

    def get_full_response(self):
        logger.info(f"Returning full response of length: {len(self.full_response)}")
        return self.full_response

    def get_tool_calls(self):
        logger.info(f"Returning {len(self.tool_calls)} tool calls")
        return self.tool_calls

    async def execute_tool_calls(self):
        from src.tools.messanger import WeddingWireMessenger
        logger.info("Starting tool execution")

        if not self.tool_calls:
            logger.info("No tool calls to execute")
            return None

        messenger = WeddingWireMessenger()

        for tool_call in self.tool_calls:
            if tool_call['name'] == 'request_pricing':
                try:
                    logger.info(f"Executing request_pricing tool call")
                    # Parse the arguments
                    args = json.loads(tool_call['arguments'])
                    logger.debug(f"Parsed arguments: {args}")

                    # Create a WeddingWireRequest object
                    request = WeddingWireRequest(
                        venue_name=args['venue_name'],
                        first_name="Assistant",  # Default values for now
                        last_name="AI",
                        phone_number="+1234567890",
                        event_month=6,
                        event_year=2025,
                        approx_guest_count=100
                    )
                    logger.info(f"Created WeddingWireRequest for venue: {request.venue_name}")

                    # Execute the tool
                    logger.info("Calling messenger.request_pricing")
                    result = await messenger.request_pricing(request)
                    logger.info("Tool execution completed successfully")
                    return result
                except Exception as e:
                    logger.error(f"Error executing tool call: {e}", exc_info=True)
                    return None
        return None


if __name__ == "__main__":
    chat = Chat()
    chat.test()
