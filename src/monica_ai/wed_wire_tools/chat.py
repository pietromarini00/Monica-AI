import asyncio
import json
import re
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

load_dotenv()


class WeddingWireMessenger:
    def __init__(
        self,
        browser_path: str = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ui: bool = False,
    ):
        self.browser_config = BrowserConfig(
            browser_binary_path=browser_path,
            headless=not ui,  # headless=True when ui=False
        )
        self.llm = ChatOpenAI(model="gpt-4o")

    async def _run_agent(self, task: str):
        browser = Browser(config=self.browser_config)
        agent = Agent(task=task, llm=self.llm, browser=browser)
        result = await agent.run()
        await browser.close()
        return result

    async def send_message(self, venue_name: str, message: str):
        task = f"""
        Go to weddingwire.com/users-login.php and make sure that we are logged in.
        Wait for the dashboard to load.
        Go to Inbox (messages).
        Open the conversation with the venue named {venue_name} in the inbox.
        Send the following message:
        '{message}'
        Close the browser.
        """
        await self._run_agent(task)

    async def retrieve_chat_history_json(self, venue_name: str) -> dict:
        task = f"""
        Go to weddingwire.com/users-login.php and make sure that we are logged in.
        Wait for the dashboard to load.
        Go to Inbox (messages).
        Open the conversation with the venue named {venue_name} in the inbox.
        Output the chat history in JSON format.
        Close the browser.
        """
        agent_history = await self._run_agent(task)
        return agent_history
