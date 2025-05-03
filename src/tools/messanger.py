import asyncio
import json
import logging
import re
from typing import Dict, Optional
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


class GuestCountCategory(str):
    """Enum-like class for guest count categories"""

    ZERO_TO_75 = "0-75"
    SEVENTY_FIVE_TO_125 = "75-125"
    ONE_TWENTY_FIVE_TO_175 = "125-175"
    ONE_SEVENTY_FIVE_PLUS = "175+"


class WeddingWireRequest(BaseModel):
    """Model for validating request pricing parameters"""

    venue_name: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: str = Field(..., pattern=r"^\+?1?\d{10,15}$")
    event_month: int = Field(..., ge=1, le=12)
    event_year: int = Field(..., ge=2023, le=2030)
    approx_guest_count: int = Field(..., ge=0)

    @validator("venue_name", "first_name", "last_name")
    def strip_and_check_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        return v


class WeddingWireMessenger:
    def __init__(
        self,
        browser_path: str = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ui: bool = False,
    ):
        """Initialize WeddingWireMessenger with browser configuration and LLM"""
        self.browser_config = BrowserConfig(
            browser_binary_path=browser_path, headless=not ui
        )
        self.llm = ChatOpenAI(model="gpt-4o")
        self.logger = logging.getLogger(__name__)

    async def _run_agent(self, task: str) -> Dict:
        """Run agent with given task and handle browser lifecycle"""
        try:
            browser = Browser(config=self.browser_config)
            agent = Agent(task=task, llm=self.llm, browser=browser)
            result = await agent.run()
            return result
        except Exception as e:
            self.logger.error(f"Error running agent: {str(e)}")
            raise
        finally:
            try:
                await browser.close()
            except Exception as e:
                self.logger.warning(f"Error closing browser: {str(e)}")

    async def send_message(self, venue_name: str, message: str) -> None:
        """Send a message to a specific venue"""
        if not venue_name.strip() or not message.strip():
            raise ValueError("Venue name and message cannot be empty")

        task = f"""
        Go to weddingwire.com/users-login.php and ensure login.
        Wait for dashboard to load.
        Navigate to Inbox.
        Open conversation with venue '{venue_name}'.
        Send message: '{message}'
        """
        try:
            await self._run_agent(task)
            self.logger.info(f"Message sent to {venue_name}")
        except Exception as e:
            self.logger.error(f"Failed to send message to {venue_name}: {str(e)}")
            raise

    async def retrieve_chat_history_json(self, venue_name: str) -> Dict:
        """Retrieve chat history with a venue in JSON format"""
        if not venue_name.strip():
            raise ValueError("Venue name cannot be empty")

        task = f"""
        Go to weddingwire.com/users-login.php and ensure login.
        Wait for dashboard to load.
        Navigate to Inbox.
        Open conversation with venue '{venue_name}'.
        Return chat history in JSON format.
        """
        try:
            result = await self._run_agent(task)
            self.logger.info(f"Retrieved chat history for {venue_name}")
            return result
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve chat history for {venue_name}: {str(e)}"
            )
            raise

    async def request_pricing(self, request: WeddingWireRequest) -> Dict:
        """Request pricing information for a venue with provided details"""
        guest_count_category = self._get_guest_count_category(
            request.approx_guest_count
        )

        task = f"""
        Search Google for "{request.venue_name} weddingwire.com"
        Wait for search results to load.
        Click on request pricing link.
        Wait for modal to load.
        Fill form with:
        First and Last Name: {request.first_name} {request.last_name}
        Phone: {request.phone_number}
        Event Month: {request.event_month}
        Event Year: {request.event_year}
        Guest Count: {guest_count_category}
        Return page source in HTML format.
        """
        try:
            result = await self._run_agent(task)
            self.logger.info(f"Retrieved pricing info for {request.venue_name}")
            return result
        except Exception as e:
            self.logger.error(
                f"Failed to request pricing for {request.venue_name}: {str(e)}"
            )
            raise

    def _get_guest_count_category(self, count: int) -> str:
        """Determine guest count category based on number of guests"""
        if count < 75:
            return GuestCountCategory.ZERO_TO_75
        elif count < 125:
            return GuestCountCategory.SEVENTY_FIVE_TO_125
        elif count < 175:
            return GuestCountCategory.ONE_TWENTY_FIVE_TO_175
        return GuestCountCategory.ONE_SEVENTY_FIVE_PLUS


# messenger = WeddingWireMessenger(ui=False)
# venue = "Riverside Farm"
# message = "We're still very interested in your venue for our wedding on Feb 1, 2027. Could you please send over more details about available packages and what's included?"

# await messenger.send_message(venue, message)
