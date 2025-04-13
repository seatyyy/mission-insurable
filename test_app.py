from asyncio import sleep
import asyncio
import streamlit as st
import hashlib
import json


# A dictionary to store ongoing tasks
tasks = {}

# Define a helper function to create and schedule async tasks
def schedule_task(key, coro):
    """Schedules an async task and stores it with a unique key."""
    if key not in tasks:
        tasks[key] = loop.create_task(coro)

# Run the event loop to process scheduled tasks
def process_tasks():
    """Process pending tasks on the event loop."""
    pending = [task for task in tasks.values() if not task.done()]
    if pending:
        loop.run_until_complete(asyncio.gather(*pending))

# Generate a unique key for tasks
def generate_task_key(*args):
    """Generate a unique hash-based key for a task."""
    return hashlib.sha256("-".join(map(str, args)).encode()).hexdigest()

async def run_browser_agent(address: str):
    await sleep(10)
    return f"run_browser_agent finished: {address}"

async def run_phone_call_agent(address: str):
    await sleep(5)
    return f"run_phone_call_agent Finished: {address}"


# Ensure there is a running event loop
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


address = st.text_input("Address")

# Submit button
submit_button = st.button("Submit")

# Display the address when submitted
if submit_button:

    # Schedule the async task
    schedule_task(
        f"task-{generate_task_key('run_browser_agent')}",
        run_browser_agent(address)
    )

    # Schedule the async task
    schedule_task(
        f"task-{generate_task_key('run_phone_call_agent')}",
        run_phone_call_agent(address)
    )

    # Process tasks
    process_tasks()

tasks_to_delete = []
for task_key, task in tasks.items():
    if task.done():  # Check if task is complete
        try:
            result = task.result()  # Get the result
            st.text(result)  # Display the predictions as JSON
            tasks_to_delete.append(task_key)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            tasks_to_delete.append(task_key)
    else:
        st.info("Tasks are still running...")

for task_key in tasks_to_delete:
    tasks.pop(task_key)