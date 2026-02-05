-- Budget Transparency Database Schema - Enhanced for CBIRR Analysis

-- ============================================================================
-- CORE TABLES (Existing - Enhanced)
-- ============================================================================

-- Table for tracking uploaded PDF files
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    county VARCHAR(100) NOT NULL,
    year VARCHAR(10) NOT NULL,
    filenames JSONB NOT NULL,
    document_type VARCHAR(50) DEFAULT 'CBIRR', -- 'CBIRR', 'Budget', 'Audit'
    file_size_bytes BIGINT,
    upload_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
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
    project_performance JSONB,
    raw_extracted JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- NEW TABLES FOR CBIRR FEATURES
-- ============================================================================

-- Document metadata for section-aware parsing
CREATE TABLE IF NOT EXISTS document_metadata (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id) ON DELETE CASCADE,
    document_type VARCHAR(50), -- 'CBIRR', 'Budget', 'Audit'
    total_pages INTEGER,
    sections JSONB, -- {section_name: {start_page, end_page, content_summary}}
    extracted_tables INTEGER DEFAULT 0,
    extracted_figures INTEGER DEFAULT 0,
    processing_time_seconds INTEGER,
    toc_extracted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sectoral allocations for detailed sector-wise tracking
CREATE TABLE IF NOT EXISTS sectoral_allocations (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    county VARCHAR(100) NOT NULL,
    year VARCHAR(10),
    sector VARCHAR(100), -- 'Health', 'Education', 'Infrastructure', 'Agriculture', 'Water', 'Governance'
    budget_allocation BIGINT DEFAULT 0,
    actual_expenditure BIGINT DEFAULT 0,
    absorption_rate DECIMAL(5,2),
    variance BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project performance tracking
CREATE TABLE IF NOT EXISTS project_performance (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    county VARCHAR(100) NOT NULL,
    year VARCHAR(10),
    sector VARCHAR(100),
    planned_projects INTEGER DEFAULT 0,
    completed_projects INTEGER DEFAULT 0,
    ongoing_projects INTEGER DEFAULT 0,
    stalled_projects INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2),
    total_project_budget BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Compliance checks against PFM Act and regulations
CREATE TABLE IF NOT EXISTS compliance_checks (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    county VARCHAR(100) NOT NULL,
    year VARCHAR(10),
    check_type VARCHAR(100), -- '30% Development Rule', 'Wage Bill Ceiling', 'OSR Target'
    rule_description TEXT,
    required_value DECIMAL(10,2),
    actual_value DECIMAL(10,2),
    compliant BOOLEAN,
    variance DECIMAL(10,2),
    variance_percent DECIMAL(5,2),
    severity VARCHAR(20), -- 'Critical', 'Warning', 'Info', 'Pass'
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- County comparisons for benchmarking
CREATE TABLE IF NOT EXISTS county_comparisons (
    id SERIAL PRIMARY KEY,
    county_a VARCHAR(100) NOT NULL,
    county_b VARCHAR(100) NOT NULL,
    fiscal_year VARCHAR(10),
    comparison_metrics JSONB, -- {metric_name: {county_a_value, county_b_value, difference, winner}}
    overall_ranking JSONB, -- {county_a_rank, county_b_rank}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User roles for RBAC
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'public', -- 'public', 'researcher', 'admin'
    permissions JSONB, -- {can_upload, can_delete, can_compare, can_export}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trail for governance
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    action VARCHAR(100), -- 'upload', 'analyze', 'compare', 'export', 'delete'
    resource_type VARCHAR(50), -- 'document', 'analysis', 'report'
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Acronym expansion for document clarity
CREATE TABLE IF NOT EXISTS acronyms (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id) ON DELETE CASCADE,
    acronym VARCHAR(20) NOT NULL,
    expansion TEXT NOT NULL,
    frequency INTEGER DEFAULT 1,
    context TEXT, -- Where it was found
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated reports tracking
CREATE TABLE IF NOT EXISTS generated_reports (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    county VARCHAR(100),
    year VARCHAR(10),
    report_type VARCHAR(50), -- 'full', 'county_specific', 'comparison', 'sectoral'
    format VARCHAR(10), -- 'pdf', 'docx', 'json'
    sections_included JSONB, -- Array of section names
    file_path TEXT,
    file_size_bytes BIGINT,
    generated_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Existing indexes
CREATE INDEX IF NOT EXISTS idx_uploads_county ON uploads(county);
CREATE INDEX IF NOT EXISTS idx_uploads_year ON uploads(year);
CREATE INDEX IF NOT EXISTS idx_analysis_county ON analysis_results(county);
CREATE INDEX IF NOT EXISTS idx_analysis_year ON analysis_results(year);

-- New indexes
CREATE INDEX IF NOT EXISTS idx_uploads_document_type ON uploads(document_type);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON uploads(upload_status);
CREATE INDEX IF NOT EXISTS idx_sectoral_county_year ON sectoral_allocations(county, year);
CREATE INDEX IF NOT EXISTS idx_sectoral_sector ON sectoral_allocations(sector);
CREATE INDEX IF NOT EXISTS idx_compliance_county_year ON compliance_checks(county, year);
CREATE INDEX IF NOT EXISTS idx_compliance_type ON compliance_checks(check_type);
CREATE INDEX IF NOT EXISTS idx_compliance_severity ON compliance_checks(severity);
CREATE INDEX IF NOT EXISTS idx_comparisons_counties ON county_comparisons(county_a, county_b);
CREATE INDEX IF NOT EXISTS idx_comparisons_year ON county_comparisons(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_acronyms_upload ON acronyms(upload_id);
CREATE INDEX IF NOT EXISTS idx_reports_analysis ON generated_reports(analysis_id);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at on uploads
CREATE TRIGGER update_uploads_updated_at BEFORE UPDATE ON uploads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger to automatically update updated_at on user_roles
CREATE TRIGGER update_user_roles_updated_at BEFORE UPDATE ON user_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate compliance status
CREATE OR REPLACE FUNCTION check_compliance_status(
    p_analysis_id INTEGER
) RETURNS TABLE(
    total_checks INTEGER,
    passed INTEGER,
    failed INTEGER,
    critical_failures INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_checks,
        COUNT(*) FILTER (WHERE compliant = TRUE)::INTEGER as passed,
        COUNT(*) FILTER (WHERE compliant = FALSE)::INTEGER as failed,
        COUNT(*) FILTER (WHERE compliant = FALSE AND severity = 'Critical')::INTEGER as critical_failures
    FROM compliance_checks
    WHERE analysis_id = p_analysis_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get county ranking by metric
CREATE OR REPLACE FUNCTION rank_counties_by_metric(
    p_year VARCHAR(10),
    p_metric VARCHAR(50) -- 'revenue', 'absorption_rate', 'osr_performance'
) RETURNS TABLE(
    rank INTEGER,
    county VARCHAR(100),
    metric_value DECIMAL
) AS $$
BEGIN
    IF p_metric = 'revenue' THEN
        RETURN QUERY
        SELECT 
            ROW_NUMBER() OVER (ORDER BY (revenue->>'revenue_actual')::BIGINT DESC)::INTEGER as rank,
            ar.county,
            (revenue->>'revenue_actual')::DECIMAL as metric_value
        FROM analysis_results ar
        WHERE ar.year = p_year
        ORDER BY metric_value DESC;
    ELSIF p_metric = 'absorption_rate' THEN
        RETURN QUERY
        SELECT 
            ROW_NUMBER() OVER (ORDER BY (computed->>'overall_absorption_percent')::DECIMAL DESC)::INTEGER as rank,
            ar.county,
            (computed->>'overall_absorption_percent')::DECIMAL as metric_value
        FROM analysis_results ar
        WHERE ar.year = p_year
        ORDER BY metric_value DESC;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for county performance summary
CREATE OR REPLACE VIEW county_performance_summary AS
SELECT 
    ar.county,
    ar.year,
    (ar.revenue->>'revenue_actual')::BIGINT as total_revenue,
    (ar.expenditure->>'total_expenditure')::BIGINT as total_expenditure,
    (ar.computed->>'overall_absorption_percent')::DECIMAL as absorption_rate,
    (ar.debt_and_liabilities->>'pending_bills_amount')::BIGINT as pending_bills,
    ar.risk_score,
    COUNT(cc.id) FILTER (WHERE cc.compliant = FALSE) as compliance_failures,
    ar.created_at
FROM analysis_results ar
LEFT JOIN compliance_checks cc ON ar.id = cc.analysis_id
GROUP BY ar.id, ar.county, ar.year, ar.revenue, ar.expenditure, ar.computed, 
         ar.debt_and_liabilities, ar.risk_score, ar.created_at;

-- View for sectoral performance
CREATE OR REPLACE VIEW sectoral_performance_summary AS
SELECT 
    sa.county,
    sa.year,
    sa.sector,
    sa.budget_allocation,
    sa.actual_expenditure,
    sa.absorption_rate,
    CASE 
        WHEN sa.absorption_rate >= 80 THEN 'Excellent'
        WHEN sa.absorption_rate >= 60 THEN 'Good'
        WHEN sa.absorption_rate >= 40 THEN 'Fair'
        ELSE 'Poor'
    END as performance_rating
FROM sectoral_allocations sa
ORDER BY sa.county, sa.year, sa.sector;
