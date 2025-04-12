import streamlit as st

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
    else:
        st.error("Please enter an address before submitting.") 