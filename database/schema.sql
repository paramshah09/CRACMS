-- ============================================================
-- Cyber Risk Assessment and Compliance Management System (CRACMS)
-- Database Schema
-- All tables use "IF NOT EXISTS" so this script can be run safely
-- every time the app starts without wiping existing data.
-- ============================================================

-- USERS
-- Basic role-based accounts (not used for full auth in this version,
-- but present so risks/records can reference a "created_by" user).
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT NOT NULL CHECK(role IN ('Admin','Risk Manager','Auditor','Viewer')) DEFAULT 'Viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RISK CATEGORIES (lookup table)
CREATE TABLE IF NOT EXISTS risk_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- RISK REGISTER
-- The core table: one row per identified risk.
CREATE TABLE IF NOT EXISTS risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    risk_code TEXT UNIQUE NOT NULL,          -- e.g. RSK-001
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER,
    asset_affected TEXT,
    likelihood INTEGER NOT NULL CHECK(likelihood BETWEEN 1 AND 5),
    impact INTEGER NOT NULL CHECK(impact BETWEEN 1 AND 5),
    risk_score INTEGER,                       -- likelihood * impact, calculated in app code
    risk_level TEXT,                          -- Low / Medium / High / Critical, derived from risk_score
    owner TEXT,
    status TEXT NOT NULL CHECK(status IN ('Open','Mitigated','Accepted','Closed')) DEFAULT 'Open',
    treatment_plan TEXT,
    identified_date DATE,
    review_date DATE,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES risk_categories(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- COMPLIANCE FRAMEWORKS
CREATE TABLE IF NOT EXISTS compliance_frameworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                       -- e.g. ISO 27001:2022, NIST CSF 2.0
    version TEXT,
    description TEXT
);

-- COMPLIANCE CONTROLS
-- Individual controls belonging to a framework.
CREATE TABLE IF NOT EXISTS compliance_controls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    framework_id INTEGER NOT NULL,
    control_ref TEXT NOT NULL,                -- e.g. A.5.1, PR.AC-1
    control_name TEXT NOT NULL,
    control_description TEXT,
    domain TEXT,                               -- e.g. Access Control, Asset Management
    FOREIGN KEY (framework_id) REFERENCES compliance_frameworks(id)
);

-- COMPLIANCE STATUS
-- Tracks how compliant the organization is against each control,
-- and can optionally link to the risk that control is meant to treat.
CREATE TABLE IF NOT EXISTS compliance_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    control_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Compliant','Partially Compliant','Non-Compliant','Not Applicable')) DEFAULT 'Non-Compliant',
    evidence TEXT,
    responsible_person TEXT,
    linked_risk_id INTEGER,
    last_assessed_date DATE,
    next_review_date DATE,
    notes TEXT,
    FOREIGN KEY (control_id) REFERENCES compliance_controls(id),
    FOREIGN KEY (linked_risk_id) REFERENCES risks(id)
);

-- AUDIT FINDINGS
-- Findings from internal/external audits. Each finding can optionally
-- link back to a specific risk via linked_risk_id.
CREATE TABLE IF NOT EXISTS audit_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finding_code TEXT UNIQUE NOT NULL,         -- e.g. AF-001
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL CHECK(severity IN ('Low','Medium','High','Critical')) DEFAULT 'Medium',
    linked_risk_id INTEGER,
    owner TEXT,
    remediation_plan TEXT,
    due_date DATE,
    status TEXT NOT NULL CHECK(status IN ('Open','In Progress','Closed','Overdue')) DEFAULT 'Open',
    FOREIGN KEY (linked_risk_id) REFERENCES risks(id)
);
