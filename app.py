import streamlit as st
import asyncio
import hashlib
from browser_agent import search
# from browser_agent import ResearchedData
from vapi import AsyncVapi


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

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Set page configuration
st.set_page_config(
    page_title="Mission Insurable AI",
    page_icon="🏠",
    layout="centered"
)
st.title("🏠 Mission Insurable AI")


st.markdown("""
<style>
    .main {
        background-color: #f9f9f9;
    }
    .property-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .property-header {
        color: #3498db;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
    }
    .property-detail {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    .detail-label {
        color: #7f8c8d;
        font-weight: 500;
    }
    .detail-value {
        color: #3498db;
        font-weight: 600;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-yes {
        background-color: #d4edda;
        color: #155724;
    }
    .badge-no {
        background-color: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Input field for address
address = st.text_input("Enter your address:")

# Submit button
submit_button = st.button("Submit")

# Function to initiate call after delay
async def delayed_call(address) -> None:
    # time.sleep(10)  # Wait for 10 seconds
    # Use Streamlit's session state to communicate back to the main thread
    st.session_state.call_initiated = True
    try:
        client = AsyncVapi(
            token='6c778c6d-e70e-4d52-879d-df8f349fe915'
        )
        assistant_overrides = {
            "recordingEnabled": False,
            "variableValues": {
                "address": address
            }
        }
        await client.calls.create(assistant_id='3a75217f-a6f9-49aa-bbaa-8800163062f9', 
                            phone_number_id='cc4e6968-f1af-49dd-ba78-b165cf5296c4',
                            assistant_overrides=assistant_overrides,
                            customer={"number":"+16504712165"})
        
        # Add a notification in the UI
        st.success("📞 Call initiated!")
        
    except Exception as e:
        st.error(f"Error initiating call: {str(e)}")

# Display the address when submitted
if submit_button:
    if address:
        st.success("Address submitted successfully!")
        call_initiated = False

        # Display the results in a modern format
        st.markdown('<div class="property-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="property-header">Property Information for {address}</div>', unsafe_allow_html=True)

        # Show a spinner while processing
        with st.spinner("Researching property information..."):
            try:
                # Run the search function with the user's address
                # result = asyncio.run(search(address))

                schedule_task(
                    f"task-search-{generate_task_key('search')}",
                    search(address)
                )

                schedule_task(
                    f"task-delayed_call-{generate_task_key('delayed_call')}",
                    delayed_call(address)
                )

                process_tasks()

                tasks_to_delete = []
                for task_key, task in tasks.items():
                    if task.done():  # Check if task is complete  
                        
                        try:
                            if 'search' in task_key:
                                result = task.result()  # Get the result
                            # st.text(result)  # Display the predictions as JSON
                            tasks_to_delete.append(task_key)
                        except Exception as e:
                            st.error(f"An error occurred: {e}")
                            tasks_to_delete.append(task_key)
                    else:
                        st.info("Tasks are still running...")

                for task_key in tasks_to_delete:
                    tasks.pop(task_key)

                # Build date
                st.markdown(
                    '<div class="property-detail">'
                    f'<span class="detail-label">Build Date</span>'
                    f'<span class="detail-value">{result.build_date}</span>'
                    '</div>', 
                    unsafe_allow_html=True
                )
                
                # Bedrooms & Bathrooms (in one row)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        '<div class="property-detail">'
                        f'<span class="detail-label">Bedrooms</span>'
                        f'<span class="detail-value">{result.bedrooms}</span>'
                        '</div>', 
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        '<div class="property-detail">'
                        f'<span class="detail-label">Bathrooms</span>'
                        f'<span class="detail-value">{result.bathrooms}</span>'
                        '</div>', 
                        unsafe_allow_html=True
                    )
                
                # Lot Size
                st.markdown(
                    '<div class="property-detail">'
                    f'<span class="detail-label">Lot Size</span>'
                    f'<span class="detail-value">{result.lot_size}</span>'
                    '</div>', 
                    unsafe_allow_html=True
                )
                
                # Construction Type
                st.markdown(
                    '<div class="property-detail">'
                    f'<span class="detail-label">Construction Type</span>'
                    f'<span class="detail-value">{result.construction_type}</span>'
                    '</div>', 
                    unsafe_allow_html=True
                )
                
                # Seismic Zone (displayed as a badge)
                seismic_badge = "badge badge-yes" if result.seismic_zone else "badge badge-no"
                seismic_text = "Yes" if result.seismic_zone else "No"
                st.markdown(
                    '<div class="property-detail">'
                    f'<span class="detail-label">In Seismic Zone</span>'
                    f'<span class="{seismic_badge}">{seismic_text}</span>'
                    '</div>', 
                    unsafe_allow_html=True
                )
                
                st.markdown('</div>', unsafe_allow_html=True)

                # asyncio.run(delayed_call())
                
            except Exception as e:
                st.error(f"An error occurred during the search: {str(e)}")
    else:
        st.error("Please enter an address before submitting.") 