#!/usr/bin/env python3
"""
Slack Fake Messages Generator
Sends fake conversation messages to a Slack channel for testing/demo purposes
"""

import os
import time
import random
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL')

# Initialize Slack client
client = WebClient(token=SLACK_BOT_TOKEN)


# Sample fake conversations - you can customize these
FAKE_CONVERSATIONS = [
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "Good morning team! Quick question about the new authentication service.",
            "I'm seeing some timeout errors in production logs. Anyone else experiencing this?",
            "The error rate is around 2.3% since yesterday's deployment.",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "Morning Alice! Yeah, I noticed that too.",
            "I think it's related to the database connection pool settings we changed.",
            "Let me check the configuration and get back to you in 10 mins.",
        ]
    },
    {
        "username": "Charlie",
        "icon_emoji": ":technologist:",
        "messages": [
            "I can confirm - we're seeing similar issues on the checkout service.",
            "Should we roll back the deployment?",
            "Our SLA is at risk if this continues.",
        ]
    },
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "Good point Charlie. Let's give Bob 10 minutes to investigate first.",
            "If we can't identify the root cause quickly, we should roll back.",
            "I'm creating an incident ticket - INC-2847",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "Found it! The connection pool max size was set to 10, should be 50.",
            "It's in the application.yml file that got overwritten during the last merge.",
            "Deploying the fix now. ETA 3 minutes.",
        ]
    },
    {
        "username": "Diana",
        "icon_emoji": ":woman_technologist:",
        "messages": [
            "Great catch Bob! 👏",
            "Let's add this to our deployment checklist so it doesn't happen again.",
            "I'll update the runbook with this troubleshooting step.",
        ]
    },
    {
        "username": "Charlie",
        "icon_emoji": ":technologist:",
        "messages": [
            "Error rate is dropping - down to 0.8% now.",
            "Looks like the fix is working!",
        ]
    },
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "Excellent! Back to normal levels. Closing the incident.",
            "Bob, can you do a quick post-mortem doc for this?",
            "Also, we should probably add automated testing for configuration changes.",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "Absolutely, I'll have the post-mortem done by EOD.",
            "And yes, good idea on the automated testing. I'll add it to our backlog.",
        ]
    },
    {
        "username": "Diana",
        "icon_emoji": ":woman_technologist:",
        "messages": [
            "Perfect team work everyone! 🎉",
            "On another note, reminder that our sprint review is tomorrow at 2 PM.",
            "Please have your demos ready.",
        ]
    },
    {
        "username": "Charlie",
        "icon_emoji": ":technologist:",
        "messages": [
            "Thanks for the reminder Diana!",
            "I'll be demoing the new analytics dashboard.",
            "Quick question - should I include the mobile responsive version or just desktop?",
        ]
    },
    {
        "username": "Diana",
        "icon_emoji": ":woman_technologist:",
        "messages": [
            "Both would be great if you have time!",
            "The stakeholders are particularly interested in the mobile experience.",
        ]
    },
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "I'll be presenting the performance improvements we made.",
            "We reduced API response time by 40% on average.",
            "Pretty excited about this one! 📊",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "That's amazing Alice! Can't wait to see the metrics.",
            "I'll demo the new user authentication flow with OAuth2 support.",
            "Still need to test the edge cases though. Anyone available to help test today?",
        ]
    },
    {
        "username": "Charlie",
        "icon_emoji": ":technologist:",
        "messages": [
            "I can help test after lunch, around 1:30 PM?",
            "Just send me the test environment URL and test cases.",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "Perfect! I'll send you an email with all the details.",
            "The test env is: https://test-auth.company.com",
            "Login with your regular credentials.",
        ]
    },
    {
        "username": "Diana",
        "icon_emoji": ":woman_technologist:",
        "messages": [
            "Great collaboration team!",
            "BTW, we got approval for the new feature roadmap for Q2.",
            "We'll be focusing on AI-powered recommendations and real-time notifications.",
        ]
    },
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "Awesome news! 🚀",
            "Do we have any initial requirements or user stories?",
            "I'd love to start thinking about the technical architecture.",
        ]
    },
    {
        "username": "Diana",
        "icon_emoji": ":woman_technologist:",
        "messages": [
            "Yes! I'll share the PRD (Product Requirements Document) by end of week.",
            "We'll do a kickoff meeting next Monday to discuss architecture.",
            "Product team has already done some user research - really interesting insights!",
        ]
    },
    {
        "username": "Charlie",
        "icon_emoji": ":technologist:",
        "messages": [
            "Looking forward to it!",
            "For the AI recommendations, are we building in-house or using a third-party service?",
        ]
    },
    {
        "username": "Diana",
        "icon_emoji": ":woman_technologist:",
        "messages": [
            "Still evaluating options. That's one thing we'll discuss in the kickoff.",
            "We're considering AWS Personalize, Google Recommendations AI, and a custom solution.",
            "Each has pros and cons we need to weigh.",
        ]
    },
    {
        "username": "Bob",
        "icon_emoji": ":man:",
        "messages": [
            "Makes sense. Cost vs customization trade-off.",
            "I have some experience with AWS Personalize from my previous company.",
            "Happy to share insights during the meeting.",
        ]
    },
    {
        "username": "Alice",
        "icon_emoji": ":woman:",
        "messages": [
            "That would be super helpful Bob!",
            "I'll start researching the other options before the meeting.",
            "Let's make sure we have a solid comparison matrix ready.",
        ]
    },
]


def send_message(channel, text, username, icon_emoji):
    """
    Send a message to Slack channel

    Args:
        channel: Slack channel ID or name
        text: Message text
        username: Display username for the message
        icon_emoji: Emoji icon for the user

    Returns:
        Response from Slack API
    """
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
            username=username,
            icon_emoji=icon_emoji
        )
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
        return None


def send_fake_conversation(channel, conversations=None, delay_range=(1, 3)):
    """
    Send a fake conversation to Slack channel

    Args:
        channel: Slack channel ID or name
        conversations: List of conversation dictionaries with username, icon_emoji, and messages
        delay_range: Tuple of (min, max) seconds to wait between messages
    """
    if conversations is None:
        conversations = FAKE_CONVERSATIONS

    print(f"Starting to send fake conversation to channel: {channel}")
    print(f"Total participants: {len(conversations)}")
    print("-" * 50)

    # Flatten all messages with their metadata
    all_messages = []
    for conv in conversations:
        for msg in conv["messages"]:
            all_messages.append({
                "text": msg,
                "username": conv["username"],
                "icon_emoji": conv["icon_emoji"]
            })

    # Send messages one by one with random delays
    for i, msg_data in enumerate(all_messages, 1):
        print(f"[{i}/{len(all_messages)}] {msg_data['username']}: {msg_data['text'][:50]}...")

        response = send_message(
            channel=channel,
            text=msg_data["text"],
            username=msg_data["username"],
            icon_emoji=msg_data["icon_emoji"]
        )

        if response:
            print(f"✓ Message sent successfully (ts: {response['ts']})")
        else:
            print(f"✗ Failed to send message")

        # Wait before sending next message (except for the last one)
        if i < len(all_messages):
            delay = random.uniform(delay_range[0], delay_range[1])
            print(f"  Waiting {delay:.1f} seconds...\n")
            time.sleep(delay)

    print("-" * 50)
    print(f"✓ Completed sending {len(all_messages)} messages!")


def test_connection():
    """Test the Slack connection and bot permissions"""
    try:
        response = client.auth_test()
        print("✓ Successfully connected to Slack!")
        print(f"  Bot Name: {response['user']}")
        print(f"  Team: {response['team']}")
        print(f"  User ID: {response['user_id']}")
        return True
    except SlackApiError as e:
        print(f"✗ Error connecting to Slack: {e.response['error']}")
        return False


def main():
    """Main function"""
    print("=" * 50)
    print("Slack Fake Messages Generator")
    print("=" * 50)
    print()

    # Validate configuration
    if not SLACK_BOT_TOKEN:
        print("✗ Error: SLACK_BOT_TOKEN not set in environment variables")
        print("  Please set it in your .env file")
        return

    if not SLACK_CHANNEL:
        print("✗ Error: SLACK_CHANNEL not set in environment variables")
        print("  Please set it in your .env file")
        return

    # Test connection
    if not test_connection():
        return

    print()
    print(f"Target channel: {SLACK_CHANNEL}")
    print()

    # Ask for confirmation
    response = input("Ready to send fake messages? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled.")
        return

    print()

    # Send fake conversation
    send_fake_conversation(
        channel=SLACK_CHANNEL,
        conversations=FAKE_CONVERSATIONS,
        delay_range=(1, 3)  # Random delay between 1-3 seconds
    )


if __name__ == "__main__":
    main()
