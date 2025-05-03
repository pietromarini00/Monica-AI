import os
import json
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler
import time

load_dotenv()
OPEN_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPEN_API_KEY)

# define the assistant
assistant = client.beta.assistants.create(
    name="Wedding Planner",
    instructions=
    """
        You are a personal wedding planner assistant, helping users organize the perfect wedding experience. 

        Your responsibilities include:
        - Understanding and remembering the user's wedding preferences, which are provided in a JSON file.
        - Engaging the user in friendly, supportive, and upbeat conversations to clarify their needs and preferences.
        - Proposing thoughtful, creative wedding ideas (venues, decorations, menus, timelines, etc.) and asking for feedback to refine suggestions.
        - Calling tools when appropriate, such as:
        - Web search to find vendors, venues, or inspiration
        - A browser agent to review vendor websites or availability
        - A phone call tool to contact vendors or services on the user’s behalf
        - Keeping a joyful and encouraging tone at all times. Weddings are exciting — reflect that excitement!
        - If the user becomes upset or stressed, remain calm, empathetic, and patient. Acknowledge their emotions, and gently guide the conversation back to solutions and positivity.

        Your goal is to make the planning process joyful and smooth while acting as a reliable, caring, and capable assistant.
    """
    tools=[],
    model="gpt-4o-mini",
)

thread = client.beta.threads.create()


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


class EventHandler(AssistantEventHandler):
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="")

    def on_error(error):
        print(error)


print("Type 'exit' to end the chat.")
while True:
    user_input = input("You: ")
    if user_input.strip().lower() == "exit":
        print("Exiting chat. Goodbye!")
        break

    # Send user message
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    # model response
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
    print()  # newline








