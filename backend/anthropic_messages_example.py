"""
Example of using Anthropic Messages API with Claude Sonnet 4
This shows the modern way to interact with Claude models
"""

import os
from anthropic import Anthropic
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ModernAnthropicClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic client with API key"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    def call_claude(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call Claude using the Messages API (for modern SDK)

        Args:
            prompt: The user prompt to send
            system_prompt: Optional system prompt for context/instructions

        Returns:
            The model's response text
        """
        try:
            logger.info(f"Calling Claude model: {self.model}")

            # Build messages list
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # Prepare kwargs for the API call
            kwargs = {
                "model": self.model,
                "max_tokens": 4000,
                "temperature": 0,
                "messages": messages
            }

            # Add system prompt if provided
            if system_prompt:
                kwargs["system"] = system_prompt

            # Make the API call using Messages API
            response = self.client.messages.create(**kwargs)

            # Extract text from response
            response_text = response.content[0].text

            logger.info(f"Successfully received response of length: {len(response_text)}")
            return response_text

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

    def call_claude_with_conversation(self, messages: list) -> str:
        """
        Call Claude with a full conversation history

        Args:
            messages: List of message dictionaries with 'role' and 'content'
                     e.g., [{"role": "user", "content": "Hello"},
                            {"role": "assistant", "content": "Hi there!"}]

        Returns:
            The model's response text
        """
        try:
            logger.info(f"Calling Claude with {len(messages)} messages")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            raise

    def call_claude_streaming(self, prompt: str):
        """
        Call Claude with streaming response

        Args:
            prompt: The user prompt to send

        Yields:
            Chunks of text as they arrive
        """
        try:
            logger.info(f"Starting streaming call to Claude model: {self.model}")

            with self.client.messages.stream(
                model=self.model,
                max_tokens=4000,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Error in streaming call: {str(e)}")
            raise


# Example usage for your LLM service
def example_for_trade_extraction():
    """
    Example showing how to use this for your trade extraction prompt
    """
    client = ModernAnthropicClient()

    # Your trade extraction prompt
    trade_extraction_prompt = """You are a company called XYZ Corp. You are receiving an email from a bank...
    [Your full prompt here]
    """

    # System prompt to ensure JSON output
    system_prompt = """You are a trade data extraction assistant.
    Always respond with valid JSON only, no markdown formatting or additional text."""

    # Example email content
    email_content = "Subject: Trade Confirmation #123456..."

    # Format the prompt with the email data
    formatted_prompt = trade_extraction_prompt.format(
        client_name="XYZ Corp",
        formatted_data=email_content
    )

    # Call Claude
    response = client.call_claude(
        prompt=formatted_prompt,
        system_prompt=system_prompt
    )

    return response


# Simple implementation that could replace your current _call_anthropic method
def simplified_call_anthropic(prompt: str, api_key: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    Simplified version that could directly replace your _call_anthropic method

    Args:
        prompt: The formatted prompt with trade extraction instructions
        api_key: Your Anthropic API key
        model: The Claude model to use

    Returns:
        The JSON response as a string
    """
    try:
        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.content[0].text

    except Exception as e:
        logger.error(f"Error calling Anthropic: {str(e)}")
        raise


if __name__ == "__main__":
    # Example test
    try:
        client = ModernAnthropicClient()

        # Simple test
        response = client.call_claude("What is 2+2? Respond with just the number.")
        print(f"Response: {response}")

        # Streaming test
        print("\nStreaming response:")
        for chunk in client.call_claude_streaming("Count from 1 to 5"):
            print(chunk, end="", flush=True)
        print()

    except Exception as e:
        print(f"Error: {e}")