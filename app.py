import streamlit as st
import asyncio
from browser_agent import search

st.title("Mission Insurable AI")

# Input field for address
address = st.text_input("Enter your address:")

# Submit button
submit_button = st.button("Submit")

# Display the address when submitted
if submit_button:
    if address:
        st.success("Address submitted successfully!")
        st.write("You entered:", address)
        
        # Show a spinner while processing
        with st.spinner("Researching property information..."):
            try:
                # Run the search function with the user's address
                result = asyncio.run(search(address))
                
                # Display the results
                st.subheader("Property Information")
                st.json(result)
            except Exception as e:
                st.error(f"An error occurred during the search: {str(e)}")
    else:
        st.error("Please enter an address before submitting.") 