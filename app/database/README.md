# Database Module

This module handles all database operations for the Stock Screener application, including models, connections, setup, and utilities.

## 📁 Structure

```
database/
├── __init__.py          # Package exports
├── connection.py        # Database connection management
├── models.py           # SQLAlchemy ORM models
├── setup.py            # Database initialization and setup
├── utils.py            # Database utilities and maintenance
└── README.md           # This file
```

## 🚀 Database Setup

### Quick Start (SQLite - Recommended for Development)

**For individual developers or quick testing:**

1. **No additional setup required!** SQLite is included with Python
2. **Automatic database creation** when you first run the app
3. **No password or server configuration needed**

```bash
# Navigate to backend directory
cd stock-screener-backend

# Activate virtual environment
source venv/bin/activate

# Test database connection
python -c "from app.database.connection import test_connection; print('✅ Connected!' if test_connection() else '❌ Connection failed')"

# Setup database tables
python -c "from app.database.setup import setup_database; setup_database()"
```

### PostgreSQL Setup (Recommended for Production/Team)

**For team development or production deployment:**

#### Option 1: Local PostgreSQL Installation

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql postgresql-contrib

   # macOS (using Homebrew)
   brew install postgresql
   brew services start postgresql

   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create Database and User:**
   ```bash
   # Connect to PostgreSQL as superuser
   sudo -u postgres psql

   # Create database and user
   CREATE DATABASE stock_screener;
   CREATE USER stock_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE stock_screener TO stock_user;
   \q
   ```

3. **Set Environment Variables:**
   ```bash
   # Create .env file in project root
   cat > .env << EOF
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=stock_screener
   DB_USER=stock_user
   DB_PASSWORD=your_secure_password
   EOF
   ```

#### Individual Developer Setup
Each developer should have their own local database:

```bash
# Developer A
DB_NAME=stock_screener_dev_a
DB_USER=dev_a
DB_PASSWORD=password_a

# Developer B  
DB_NAME=stock_screener_dev_b
DB_USER=dev_b
DB_PASSWORD=password_b
```


```bash
# Development
cp .env.example .env.dev

# Production  
cp .env.example .env.prod

# Testing
cp .env.example .env.test
```

**Example .env file:**
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_screener
DB_USER=postgres
DB_PASSWORD=your_password

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

### Verification Steps

**After setup, verify everything works:**

```bash
# 1. Test connection
python -c "from app.database.connection import test_connection; print('✅ Connection OK' if test_connection() else '❌ Connection Failed')"

# 2. Setup database
python -c "from app.database.setup import setup_database; setup_database()"

# 3. Verify tables created
python -c "from app.database.utils import get_database_stats; print(get_database_stats())"

# 4. Test basic operations
python -c "
from app.database import get_db_session, Stock
with get_db_session() as db:
    count = db.query(Stock).count()
    print(f'✅ Database working! Stock count: {count}')
"
```

## 🗄️ Models

### Stock
- **symbol** (Primary Key): Stock ticker symbol
- **name**: Company name
- **sector**: Industry sector
- **industry**: Specific industry
- **market_cap**: Market capitalization
- **current_price**: Current stock price
- **pe_ratio**: Price-to-earnings ratio
- **dividend_yield**: Dividend yield
- **beta**: Beta coefficient
- **info**: JSON field for additional yfinance data
- **created_at/updated_at**: Timestamps

### HistoricalPrice
- **id** (Primary Key): Auto-incrementing ID
- **symbol** (Foreign Key): References Stock.symbol
- **date**: Price date
- **open/high/low/close**: OHLC prices
- **volume**: Trading volume
- **adj_close**: Adjusted close price
- **created_at**: Timestamp

### ScreeningResult
- **id** (Primary Key): Auto-incrementing ID
- **criteria_hash**: Hash of screening criteria for caching
- **criteria**: Original screening criteria (JSON)
- **results**: Screening results (JSON)
- **index_used**: Stock index used
- **execution_time**: Time taken to execute
- **created_at/expires_at**: Timestamps for cache management

## 🔧 Usage

### Basic Setup
```python
from app.database import setup_database, get_db_session

# Initialize database
setup_database()

# Use database session
with get_db_session() as db:
    stocks = db.query(Stock).all()
```

### Database Operations
```python
from app.database import get_db_session, Stock, HistoricalPrice

# Add a stock
with get_db_session() as db:
    stock = Stock(
        symbol='AAPL',
        name='Apple Inc.',
        sector='Technology',
        market_cap=2000000000000
    )
    db.add(stock)

# Query stocks
with get_db_session() as db:
    tech_stocks = db.query(Stock).filter(Stock.sector == 'Technology').all()
```

### Utilities
```python
from app.database import backup_database, reset_database, get_database_stats

# Create backup
backup_file = backup_database()

# Get statistics
stats = get_database_stats()

# Reset database (⚠️ Destructive!)
reset_database()
```

## ⚙️ Configuration

Database configuration is handled in `app/config.py`:

```python
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "stock_screener")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
```

## 🔒 Security

- Database credentials are loaded from environment variables
- No hardcoded passwords in the codebase
- Connection pooling with automatic cleanup
- Prepared statements prevent SQL injection

## 📊 Performance

- Indexes on frequently queried columns
- Connection pooling for efficient resource usage
- Composite indexes for complex queries
- Automatic connection verification

## 🛠️ Maintenance

### Regular Tasks
1. **Cache Cleanup**: Remove expired screening results
2. **Database Optimization**: Run VACUUM/ANALYZE
3. **Backup Creation**: Regular database backups

### Commands
```bash
# Test database connection
python -m app.database.connection

# Setup database
python -m app.database.setup

# Get database stats
python -m app.database.utils

# Create backup
python -c "from app.database.utils import backup_database; backup_database()"
```

## 🚨 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check database credentials in environment variables
   - Verify database server is running
   - Check network connectivity

2. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration

3. **Performance Issues**
   - Run database optimization
   - Check index usage
   - Monitor connection pool usage

### Debug Mode
Enable SQL logging by setting `echo=True` in `connection.py`:
```python
engine = create_engine(get_database_url(), echo=True)
```

### PostgreSQL-Specific Issues

1. **Authentication Failed**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Reset postgres user password
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'new_password';"
   ```

2. **Permission Denied**
   ```bash
   # Grant permissions
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE stock_screener TO your_user;"
   ```

3. **Po 