# Policy Navigator Agent

A Multi-Agent RAG System for Government Regulation Search using aiXplain SDK

##  Project Overview

The Policy Navigator Agent is an intelligent system designed to help users navigate complex government regulations, compliance policies, and public health guidelines. Built using the aiXplain SDK, it provides real-time policy information, case law analysis, and compliance guidance through multiple integrated tools and data sources.

### Key Features

-  Intelligent Policy Search: Vector-based search through policy documents using ChromaDB
-  Real-time Policy Status: Integration with Federal Register API for up-to-date policy information
-  Case Law Analysis: CourtListener API integration for relevant legal precedents
-  Compliance Analysis: Custom analysis tools for extracting compliance requirements
-  Slack Integration: Automated notifications and reminders via Slack
-  Multi-Agent Architecture: Coordinated agents specializing in different aspects of policy research

##  Architecture

### Agent Capabilities

The Policy Navigator Agent can handle queries like:

1. **Policy Status Checks**
   - "Is Executive Order 14067 still in effect or has it been repealed?"
   - "What's the current status of GDPR compliance requirements?"

2. **Case Law Research**
   - "Has Section 230 ever been challenged in court? What was the outcome?"
   - "Find court rulings related to cryptocurrency regulations"

3. **Compliance Analysis**
   - "What are the compliance requirements for small businesses under this policy?"
   - "When does this policy take effect and what are the deadlines?"

4. **Regulatory Updates**
   - Real-time notifications via Slack for policy changes
   - Scheduled compliance reminders

### Technical Components

1. **RAG Pipeline**: Vector-based retrieval using ChromaDB and sentence transformers
2. **Data Sources**: 
   - Policy dataset (sample government regulations)
   - EPA website scraping for environmental policies
3. **Tool Integration**:
   - Federal Register API (marketplace tool)
   - Custom Python analysis tool
   - CourtListener API for case law
   - Slack integration for notifications

##  Quick Start

### Prerequisites

- Python 3.8+
- aiXplain API key (optional, for full aiXplain integration)
- Slack Bot Token (optional, for Slack notifications)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd policy-navigator-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize the agent**
   ```bash
   python cli.py setup
   ```

### Basic Usage

#### Command Line Interface

```bash
# Ask a question
python cli.py query "Is Executive Order 14067 still in effect?"

# Interactive mode
python cli.py interactive

# Check agent status
python cli.py status

# Send Slack notification
python cli.py notify --policy-title "New Regulation" --update-type "New" --details "Important update"

# Set compliance reminder
python cli.py remind --requirement "Implement new procedures" --deadline "2024-06-01"
```

#### Python API

```python
from src.policy_navigator_agent import PolicyNavigatorAgent

# Initialize the agent
agent = PolicyNavigatorAgent()

# Ask a question
response = agent.query("What are the compliance requirements for GDPR?")
print(response)

# Check component status
status = agent.test_components()
print(status)
```

##  Data Sources

### 1. Policy Dataset
- **Source**: Curated dataset of government regulations
- **Content**: Executive orders, federal laws, regulations (GDPR, HIPAA, etc.)
- **Format**: JSON with structured metadata

### 2. Website Scraping
- **Source**: EPA website (environmental policies)
- **Content**: Clean Air Act, Clean Water Act, RCRA
- **Method**: BeautifulSoup-based scraping with respectful delays

##  Tool Integration

### 1. Federal Register API (Marketplace Tool)
- **Purpose**: Real-time policy status checks
- **Capabilities**: 
  - Executive order status verification
  - Recent regulation searches
  - Document retrieval by number
- **Implementation**: REST API integration with error handling

### 2. Custom Policy Analysis Tool
- **Purpose**: Extract compliance requirements from documents
- **Features**:
  - Mandatory/optional requirement identification
  - Deadline extraction
  - Penalty identification
  - Stakeholder analysis
- **Technology**: NLP-based text analysis with regex patterns

### 3. CourtListener API
- **Purpose**: Case law and legal precedent research
- **Features**:
  - Case law search by topic
  - Court ruling summaries
  - Legal outcome analysis
- **Fallback**: Mock data for demonstration when API unavailable

### 4. Slack Integration (External Tool)
- **Purpose**: Notifications and team communication
- **Features**:
  - Policy update notifications
  - Compliance deadline reminders
  - Query response sharing
  - Channel management


##  Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# aiXplain Configuration (required for full integration)
AIXPLAIN_API_KEY=your_aixplain_api_key_here

# External Integrations (optional)
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_DEFAULT_CHANNEL=#policy-updates

# Database Configuration
CHROMA_DB_PATH=./data/chroma_db
```

### Logging Configuration

The system uses structured logging with multiple handlers:
- Console output for development
- Rotating file logs for production
- JSON structured logs for analysis
- Error-specific log files

##  Example Usage Scenarios

### 1. Policy Status Check
```bash
python cli.py query "Is Executive Order 14067 still in effect?"
```

**Response**: Real-time status from Federal Register API with publication date, current status, and any amendments.

### 2. Compliance Analysis
```bash
python cli.py query "What are the compliance requirements for small businesses under GDPR?"
```

**Response**: Structured analysis of mandatory requirements, deadlines, and penalties extracted from policy documents.

### 3. Case Law Research
```bash
python cli.py query "Has Section 230 ever been challenged in court?"
```

**Response**: Relevant court cases with summaries, outcomes, and legal implications.

### 4. Slack Notifications
```bash
python cli.py notify --policy-title "GDPR Amendment" --update-type "Amendment" --details "New data processing requirements effective June 2024"
```

**Result**: Formatted notification sent to configured Slack channel.

##  Testing

Run the test suite to verify all components:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_policy_navigator.py::TestVectorStore -v

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Coverage

- Data ingestion and processing
- Vector storage and retrieval
- External API integrations
- Agent query processing
- Error handling scenarios

##  Deployment

### Local Development
```bash
# Install in development mode
pip install -e .

# Run with debugging
python cli.py setup --initialize-data
python cli.py interactive
```

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Demo
Below are sample demonstrations of the Policy Navigator Agent in action using the CLI interface:

1. Query Example

<img width="1277" height="162" alt="image" src="https://github.com/user-attachments/assets/51d601bd-b0d2-43a8-9030-681599fa0397" />

Output:

<img width="1480" height="116" alt="Screenshot 2025-08-25 115234" src="https://github.com/user-attachments/assets/8086c397-633a-4f14-8122-7ad51aa7cdf0" />


2. Policy Notification Example

<img width="1548" height="177" alt="Screenshot 2025-08-25 102726" src="https://github.com/user-attachments/assets/76b612ca-1132-4e6e-9fcf-5305c7214c7a" />

Output:
<img width="1372" height="162" alt="image" src="https://github.com/user-attachments/assets/2e10ad60-d5ea-45a6-9a6f-a4ac620a0cf5" />






