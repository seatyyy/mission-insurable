# Address Input App

A simple Streamlit application that allows users to input an address and submit it.

## Setup

1. Install the required packages:
```
pip install -r requirements.txt
```

2. Run the application:

If you want to use CDP, start chrome in CDP mode: 
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

```
streamlit run app.py
```

The app will open in your default web browser at http://localhost:8501.

## Usage

1. Enter your address in the text input field
2. Click the "Submit" button
3. The app will display the submitted address 