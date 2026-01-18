-- Budget Transparency Database Schema

-- Table for tracking uploaded PDF files
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    county VARCHAR(100) NOT NULL,
    year VARCHAR(10) NOT NULL,
    filenames JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id) ON DELETE CASCADE,
    county VARCHAR(100) NOT NULL,
    year VARCHAR(10),
    revenue JSONB,
    expenditure JSONB,
    debt_and_liabilities JSONB,
    computed JSONB,
    intelligence JSONB,
    summary_text TEXT,
    risk_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_uploads_county ON uploads(county);
CREATE INDEX IF NOT EXISTS idx_uploads_year ON uploads(year);
CREATE INDEX IF NOT EXISTS idx_analysis_county ON analysis_results(county);
CREATE INDEX IF NOT EXISTS idx_analysis_year ON analysis_results(year);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_uploads_updated_at BEFORE UPDATE ON uploads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
