import os
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler
from src.ui import OnboardingForm
from src.tools.messanger import WeddingWireRequest, tool_config
import json
import logging
from typing_extensions import override
import asyncio

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
        event_handler = EventHandler(self.client)
        logger.info("Starting assistant stream")
        try:
            with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                event_handler=event_handler,
            ) as stream:
                logger.info("Stream created, waiting for completion...")
                stream.until_done()
                logger.info("Stream completed")
        except Exception as e:
            logger.error(f"Error during streaming: {e}", exc_info=True)
            raise

        # Get the full response
        full_response = event_handler.get_full_response()
        logger.info(f"LLM Completion length: {len(full_response)}")
        logger.info(f"LLM Completion content:\n{full_response}")

        return full_response

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
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.full_response = ""
        self.tool_calls = []
        self.run_id = None
        self.thread_id = None
        self._event_loop = asyncio.get_event_loop()
        logger.info("EventHandler initialized")

    @override
    def on_event(self, event):
        logger.info(f"Received event: {event.event}")
        if event.event == 'thread.run.requires_action':
            self.run_id = event.data.id
            self.thread_id = event.data.thread_id
            # Schedule the async handler in the event loop
            self._event_loop.create_task(self.handle_requires_action(event.data, self.run_id))

    async def handle_requires_action(self, data, run_id):
        logger.info("Handling requires_action event")
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            logger.info(f"Processing tool call: {tool.function.name}")
            if tool.function.name == "request_pricing":
                try:
                    # Parse the arguments
                    args = json.loads(tool.function.arguments)
                    logger.info(f"Tool call arguments: {args}")

                    # Create a WeddingWireRequest object
                    from src.tools.messanger import WeddingWireRequest, WeddingWireMessenger
                    request = WeddingWireRequest(
                        venue_name=args['venue_name'],
                        first_name="Assistant",  # Default values for now
                        last_name="AI",
                        phone_number="+1234567890",
                        event_month=6,
                        event_year=2025,
                        approx_guest_count=100
                    )

                    # Execute the tool
                    messenger = WeddingWireMessenger()
                    result = await messenger.request_pricing(request)

                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": json.dumps(result)
                    })
                except Exception as e:
                    logger.error(f"Error executing tool call: {e}", exc_info=True)
                    tool_outputs.append({
                        "tool_call_id": tool.id,
                        "output": f"Error executing tool: {str(e)}"
                    })

        # Submit all tool_outputs at the same time
        await self.submit_tool_outputs(tool_outputs, run_id)

    async def submit_tool_outputs(self, tool_outputs, run_id):
        logger.info("Submitting tool outputs")
        # Just submit the tool outputs without waiting for a response
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs
        )
        # Add our simple response
        self.full_response = "I sent a message to request more information!"
        logger.info("Tool outputs submitted and response set")

    def on_text_delta(self, delta, snapshot):
        logger.debug(f"Received text delta: {delta.value}")
        self.full_response += delta.value
        logger.debug(f"Current full response: {self.full_response}")

    def on_error(self, error):
        logger.error(f"Error in EventHandler: {error}", exc_info=True)

    def get_full_response(self):
        logger.info(f"Returning full response of length: {len(self.full_response)}")
        return self.full_response

    def get_tool_calls(self):
        logger.info(f"Returning {len(self.tool_calls)} tool calls")
        return self.tool_calls


if __name__ == "__main__":
    chat = Chat()
    chat.test()
