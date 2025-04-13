# Mission Insurable AI

A comprehensive application for property research and insurance assistance. The app allows insurance agencies to input an address and receive detailed property information automatically while offering automated calling functionality for insurance consultations.

## Features

### Property Research
- Extracts detailed property information from multiple sources
- Searches government websites and databases for property details
- Displays information in a clean, modern interface
- Supports data points like:
  - Building date
  - Construction type
  - Lot size
  - Number of bedrooms and bathrooms
  - Seismic zone data
  - And more

### Automated Calling
- Integration with Vapi API for automated phone calls
- Initiates calls to government officials on behalf of insurance agency
- Provides context-aware conversation based on property details

### Email Processing
- Monitors email inbox for property-related documents
- Extracts key information from email attachments
- Uses AI for document analysis

## Setup

### Prerequisites
- Python 3.9+
- Google Chrome (for browser automation)
- Vapi API credentials
- OpenAI API key (for property data analysis)
- Anthropic API key (for document analysis)
- Email credentials (for email monitoring)

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/mission-insurable-ai.git
cd mission-insurable-ai
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Configure environment variables:
   - Copy the `.env.example` file to `.env`
   - Fill in your API keys and credentials

```
OPENAI_API_KEY="your-openai-key"
EMAIL='your-email@example.com'
PASSWORD='your-email-password'
IMAP_SERVER='imap.gmail.com'
SAVE_ATTACHMENTS_TO='./attachments'
SUBJECT_TO_SEARCH="200 Madison records request"
ANTHROPIC_API_KEY="your-anthropic-key"
```

### Running the Application

1. Start Chrome in CDP mode (for browser automation):
```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

2. Run the Streamlit application:
```
streamlit run app.py
```

The app will open in your default web browser at http://localhost:8501.

## Usage

### Property Research
1. Enter an address in the text input field
2. Click the "Submit" button
3. The application will:
   - Research property information using browser automation
   - Display the results in a modern interface
   - Initiate a call via Vapi after 10 seconds (if configured)

### Email Processing
1. Click the "Refresh email inbox" button
2. The application will:
   - Check your email for messages with the configured subject
   - Download any attachments
   - Extract and display key information

## Technical Details

### Architecture
- **Browser Agent**: Automates web browsing to extract property information
- **Email Agent**: Monitors and processes email attachments
- **Vapi Integration**: Handles automated calling functionality
- **Streamlit UI**: Provides the user interface

### Concurrency
- Uses asyncio for concurrent operations
- Property search and call initiation run in parallel

## Configuration Options

### Browser Agent
- `USE_MOCK_DATA`: Set to "True" to use mock data instead of live web searches
- `DEMO`: Set to "True" for simplified demo mode

### Email Agent
- `EMAIL`: Email address to monitor
- `PASSWORD`: Email password
- `IMAP_SERVER`: IMAP server address
- `SAVE_ATTACHMENTS_TO`: Directory to save attachments
- `SUBJECT_TO_SEARCH`: Email subject to filter by

### Vapi Configuration
- Update the Vapi token and assistant IDs in the app.py file
