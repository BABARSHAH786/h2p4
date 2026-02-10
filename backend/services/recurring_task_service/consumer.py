"""Kafka consumer for task-events topic.

This module consumes task.completed events and delegates to the handler.
"""
import json
import asyncio
from typing import Optional
import httpx
from handler import handle_recurring_task_completion


DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "pubsub"
TOPIC_NAME = "task-events"
CONSUMER_GROUP = "recurring-task-service"

consumer_running = False


async def start_consumer():
    """Start consuming events from task-events topic via Dapr Pub/Sub."""
    global consumer_running
    consumer_running = True

    print(f"Starting Kafka consumer for topic: {TOPIC_NAME}")

    # Subscribe to task-events topic via Dapr
    async with httpx.AsyncClient() as client:
        while consumer_running:
            try:
                # Poll for messages using Dapr Pub/Sub
                response = await client.get(
                    f"http://localhost:{DAPR_HTTP_PORT}/v1.0/subscribe",
                    timeout=30.0
                )

                if response.status_code == 200:
                    events = response.json()
                    for event in events:
                        await process_event(event)

                # Wait before next poll
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error consuming events: {e}")
                await asyncio.sleep(5)  # Backoff on error


async def process_event(event: dict):
    """Process a single event from Kafka."""
    try:
        event_type = event.get("event_type")

        # Only process task.completed events
        if event_type == "task.completed":
            data = event.get("data", {})

            # Check if task has recurrence
            recurrence = data.get("recurrence", "none")
            if recurrence != "none":
                await handle_recurring_task_completion(event)

    except Exception as e:
        print(f"Error processing event: {e}")


async def stop_consumer():
    """Stop the Kafka consumer."""
    global consumer_running
    consumer_running = False
    print("Stopping Kafka consumer")
