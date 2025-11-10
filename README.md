# Tech Salary Negotiator

An AI-powered salary negotiation helper for tech professionals. Upload your offer letter, get comprehensive market analysis, and receive personalized negotiation scripts.

## Features

- 📄 **PDF Offer Letter Parsing**: Automatically extract compensation details from offer letters
- 🧠 **AI-Powered Analysis**: Uses Google Gemini 2.0 for comprehensive offer evaluation
- 📊 **Market Data Comparison**: Compare your offer against real market data
- 📧 **Personalized Scripts**: Get three different negotiation email templates
- 🎯 **Negotiation Targets**: Conservative, realistic, and aggressive compensation goals
- 💡 **Actionable Insights**: Leverage points and talking points for negotiation

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Python ORM for database operations
- **SQLite** - Lightweight database for salary data
- **Google Gemini 2.0 Flash** - Advanced AI for analysis and script generation
- **PyPDF2** - PDF parsing for offer letters

### Frontend
- **React 18** - Modern UI library
- **TailwindCSS** - Utility-first CSS framework
- **Vite** - Fast development build tool
- **Lucide React** - Beautiful icons

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API key
- SQLite (included with Python)

### 1. Clone and Setup Backend

```bash
# Clone the repository
git clone <repository-url>
cd tech-salary-negotiator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
DATABASE_URL=sqlite:///./salary_negotiator.db
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
```

### 3. Set Up Database

```bash
# Initialize SQLite database and sample data
python init_db.py
```

### 4. Start Backend Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 5. Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Analyze Offer Letter
```
POST /api/analyze-offer
Content-Type: multipart/form-data

Form data:
- file: PDF offer letter
- years_experience: number
- tech_stack: comma-separated string
- current_salary: number (optional)
- has_competing_offers: boolean (optional)
```

### Contribute Salary Data
```
POST /api/contribute-salary
Content-Type: multipart/form-data

Form data:
- job_title: string
- company: string
- location: string
- base_salary: number
- bonus: number (optional)
- equity_value: number (optional)
- years_experience: number
- tech_stack: comma-separated string
```

### Health Check
```
GET /api/health
```

## Project Structure

```
tech-salary-negotiator/
├── main.py                 # FastAPI application entry point
├── database.py            # Database initialization and connections
├── models.py              # Pydantic data models
├── init_db.py             # Database setup script
├── services/              # Business logic services
│   ├── offer_parser.py    # PDF parsing and data extraction
│   ├── salary_analyzer.py # AI-powered offer analysis
│   ├── market_data.py     # Market data engine
│   ├── script_generator.py # Negotiation script generation
│   └── salary_contribution.py # Anonymous salary data collection
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── App.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   └── AnalysisResults.jsx
│   │   ├── services/
│   │   │   └── api.js     # API client
│   │   ├── App.jsx        # Main application component
│   │   └── main.jsx       # React entry point
│   ├── package.json
│   └── vite.config.js
├── requirements.txt        # Python dependencies
└── README.md
```

## How It Works

1. **Upload Offer Letter**: Users upload their PDF offer letter
2. **AI Parsing**: Gemini AI extracts salary, bonus, equity, and job details
3. **Market Analysis**: System compares offer against crowd-sourced market data
4. **Comprehensive Analysis**: AI provides detailed assessment with leverage points
5. **Script Generation**: Three personalized negotiation email templates are created
6. **Actionable Insights**: Users get specific negotiation strategies and talking points

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add appropriate error handling
- Write tests for new features
- Update documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed information
3. Join our community discussions

## Roadmap

- [ ] User authentication and profiles
- [ ] Advanced filtering and search for market data
- [ ] Industry-specific market data
- [ ] Mobile app development
- [ ] Integration with LinkedIn for easy profile import
- [ ] Real-time negotiation coaching
- [ ] Company reputation and culture insights

## Privacy & Security

- All uploaded documents are processed securely
- Personal information is never shared with third parties
- Offer letters are not permanently stored
- Salary data is anonymized before contribution
- GDPR and CCPA compliant

---

Built with ❤️ to help tech professionals negotiate better salaries# tech-salary-negotiator
