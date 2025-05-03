import os
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler
from src.ui import OnboardingForm

load_dotenv()
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")




class Chat:
    def __init__(self, onboarding_info: OnboardingForm):
        self.client = OpenAI(api_key=OPEN_API_KEY)
        # define the assistant
        self.assistant = self.client.beta.assistants.create(
            name="Wedding Planner",
            instructions="""
                You are a personal wedding planner assistant, helping users organize the perfect wedding experience.

                Your responsibilities include:
                - Understanding and remembering the user's wedding preferences, which are provided in a JSON file.
                - Engaging the user in friendly, supportive, and upbeat conversations to clarify their needs and preferences.
                - Proposing thoughtful, creative wedding ideas (venues, decorations, menus, timelines, etc.) and asking for feedback to refine suggestions.
                - Calling tools when appropriate, such as:
                - Web search to find vendors, venues, or inspiration
                - A browser agent to review vendor websites or availability
                - A phone call tool to contact vendors or services on the user's behalf
                - Keeping a joyful and encouraging tone at all times. Weddings are exciting — reflect that excitement!
                - If the user becomes upset or stressed, remain calm, empathetic, and patient. Acknowledge their emotions, and gently guide the conversation back to solutions and positivity.

                Your goal is to make the planning process joyful and smooth while acting as a reliable, caring, and capable assistant.
            """,
            tools=[],
            model="gpt-4o-mini"
        )

        self.thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=f"User onboarding info: {str(onboarding_info.model_dump())}",
        )


    def run(self, user_message: str) -> str:
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message,
        )
        # model response
        event_handler = EventHandler()
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()

        return event_handler.get_full_response()

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

    def on_text_delta(self, delta, snapshot):
        # print(delta.value, end="")
        self.full_response += delta.value

    def on_error(self, error):
        print(error)

    def get_full_response(self):
        return self.full_response


if __name__ == "__main__":
    chat = Chat()
    chat.test()
