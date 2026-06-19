-- ============================================================
-- CRACMS Seed Data
-- Realistic college ERP / IT infrastructure scenario.
-- Run against a freshly created database (relies on default
-- AUTOINCREMENT ids starting at 1, in insertion order below).
-- ============================================================

-- ------------------------------------------------------------
-- RISK CATEGORIES (5)
-- ------------------------------------------------------------
INSERT INTO risk_categories (name, description) VALUES
('Network Security', 'Risks related to campus network infrastructure, Wi-Fi, and connectivity'),
('Application Security', 'Risks in the ERP, LMS, and other web-based college applications'),
('Data Privacy', 'Risks involving exposure or mishandling of student and staff personal data'),
('Physical Security', 'Risks related to physical access to IT infrastructure and facilities'),
('Third-Party / Vendor Risk', 'Risks introduced by external vendors and outsourced services');

-- ------------------------------------------------------------
-- COMPLIANCE FRAMEWORKS (3)
-- ------------------------------------------------------------
INSERT INTO compliance_frameworks (name, version, description) VALUES
('ISO/IEC 27001', '2022', 'International standard for information security management systems'),
('NIST Cybersecurity Framework', 'CSF 2.0', 'Voluntary framework for managing cybersecurity risk'),
('Digital Personal Data Protection Act', '2023', 'Indian law governing processing of digital personal data');

-- ------------------------------------------------------------
-- RISKS (25)
-- ------------------------------------------------------------
INSERT INTO risks (risk_code, title, description, category_id, asset_affected, likelihood, impact, risk_score, risk_level, owner, status, treatment_plan, identified_date, review_date) VALUES
('RSK-001', 'SQL injection vulnerability in fee payment gateway', 'Penetration testing revealed unsanitized input fields allowing SQL injection on the online fee payment module.', 2, 'Student Fee Payment Portal', 4, 5, 20, 'Critical', 'Application Security Team', 'Open', 'Conduct code review and implement parameterized queries across all payment endpoints.', '2025-09-12', '2026-07-15'),
('RSK-002', 'Outdated ERP core module with unpatched known CVEs', 'The core ERP module is running a version with several publicly disclosed vulnerabilities.', 2, 'College ERP System', 4, 4, 16, 'High', 'IT Infrastructure Team', 'Mitigated', 'Scheduled patch deployment during the next maintenance window.', '2025-08-05', '2026-08-01'),
('RSK-003', 'Weak password policy enforced on student portal', 'Student accounts can be created with short, non-complex passwords, increasing credential-stuffing risk.', 2, 'Student Self-Service Portal', 4, 3, 12, 'High', 'Application Security Team', 'Open', 'Enforce minimum 12-character complex passwords with account lockout after failed attempts.', '2025-10-01', '2026-07-01'),
('RSK-004', 'No multi-factor authentication for faculty admin panel', 'Faculty administrative accounts rely on single-factor password authentication only.', 2, 'Faculty Admin Portal', 3, 5, 15, 'High', 'IT Infrastructure Team', 'Open', 'Roll out TOTP-based MFA for all faculty and admin accounts.', '2025-09-20', '2026-09-01'),
('RSK-005', 'Default credentials left active on core network switches', 'An internal audit found vendor default usernames/passwords still active on critical switches.', 1, 'Core Network Switches', 3, 5, 15, 'High', 'Network Admin', 'Mitigated', 'Reset all default credentials and enforce a credential rotation policy.', '2025-07-18', '2026-07-18'),
('RSK-006', 'Open Wi-Fi network in hostel blocks without authentication', 'Hostel Wi-Fi access points broadcast an open network with no login or encryption.', 1, 'Hostel Wi-Fi Network', 5, 3, 15, 'High', 'Network Admin', 'Open', 'Implement WPA2-Enterprise with per-student login credentials.', '2025-11-02', '2026-08-15'),
('RSK-007', 'Outdated firmware on campus CCTV camera systems', 'CCTV units across campus are running firmware several versions behind the vendor''s latest release.', 4, 'Campus CCTV Network', 3, 3, 9, 'Medium', 'Facilities & Security Team', 'Open', 'Schedule firmware updates with vendor support team.', '2025-12-10', '2026-09-10'),
('RSK-008', 'Unrestricted physical access to main server room', 'The server room door uses a shared mechanical key with no access logging.', 4, 'Main Server Room', 2, 5, 10, 'High', 'Facilities & Security Team', 'Mitigated', 'Install biometric access control and CCTV coverage at the server room entrance.', '2025-08-22', '2026-08-22'),
('RSK-009', 'No documented disaster recovery plan for ERP database', 'There is no tested or documented disaster recovery procedure for the primary ERP database.', 1, 'ERP Database Server', 3, 5, 15, 'High', 'IT Infrastructure Team', 'Open', 'Draft and test a formal disaster recovery and backup restoration plan.', '2025-10-15', '2026-07-30'),
('RSK-010', 'Ransomware exposure on exam result publishing server', 'The exam result server shares a network segment with general-purpose workstations, increasing ransomware spread risk.', 2, 'Exam Result Server', 3, 5, 15, 'High', 'IT Infrastructure Team', 'Open', 'Isolate the server on a dedicated VLAN and enable offline backups.', '2025-09-05', '2026-08-05'),
('RSK-011', 'Unencrypted backups of student personal data', 'Nightly database backups containing student PII are stored on disk without encryption.', 3, 'Student Records Backup Storage', 3, 4, 12, 'High', 'Data Protection Officer', 'Open', 'Enable AES-256 encryption for all backup volumes.', '2025-11-20', '2026-09-20'),
('RSK-012', 'Third-party canteen payment app storing card data insecurely', 'The outsourced canteen payment app logs full card numbers in plaintext application logs.', 5, 'Canteen Payment Application', 3, 4, 12, 'High', 'Procurement & Vendor Management', 'Open', 'Require vendor PCI-DSS compliance certification before continued use.', '2025-12-01', '2026-10-01'),
('RSK-013', 'Insider threat from IT staff holding excessive admin privileges', 'Several IT support staff retain full administrative access to ERP and LMS systems beyond their role needs.', 3, 'ERP and LMS Admin Accounts', 2, 4, 8, 'Medium', 'IT Infrastructure Team', 'Accepted', 'Implement role-based access control with quarterly access reviews.', '2025-08-28', '2026-08-28'),
('RSK-014', 'Misconfigured cloud storage exposing shared drive links publicly', 'Several Google Workspace shared drives were found set to "anyone with the link" instead of restricted access.', 3, 'Google Workspace Shared Drives', 4, 3, 12, 'High', 'Data Protection Officer', 'Mitigated', 'Audit sharing permissions and set "restricted" as the default sharing setting.', '2025-10-30', '2026-07-30'),
('RSK-015', 'Outdated Moodle LMS plugins with known vulnerabilities', 'Three installed Moodle plugins have publicly disclosed CVEs with available patches not yet applied.', 2, 'Moodle Learning Management System', 3, 3, 9, 'Medium', 'Application Security Team', 'Open', 'Update all plugins and remove unused or unsupported ones.', '2025-09-25', '2026-08-25'),
('RSK-016', 'Legacy WEP encryption still used in older academic block Wi-Fi', 'Wi-Fi access points in Academic Block C still broadcast using deprecated WEP encryption.', 1, 'Academic Block Wi-Fi (Block C)', 3, 3, 9, 'Medium', 'Network Admin', 'Open', 'Migrate all access points in Block C to WPA3.', '2025-12-15', '2026-09-15'),
('RSK-017', 'No backup mechanism for biometric attendance system data', 'The biometric attendance system has no scheduled backup of enrollment or attendance records.', 4, 'Biometric Attendance System', 2, 3, 6, 'Medium', 'Facilities & Security Team', 'Open', 'Configure daily automated backups to secure off-site storage.', '2026-01-10', '2026-10-10'),
('RSK-018', 'Phishing emails targeting student institutional email accounts', 'Multiple phishing campaigns impersonating the registrar''s office have been reported by students.', 3, 'Student Email System', 4, 2, 8, 'Medium', 'IT Infrastructure Team', 'Open', 'Deploy enhanced email filtering and run a student phishing awareness campaign.', '2025-11-05', '2026-08-05'),
('RSK-019', 'Lack of patch management process for computer lab systems', 'Computer lab workstations are patched manually and irregularly, leaving known gaps unaddressed.', 2, 'Computer Lab Workstations', 4, 2, 8, 'Medium', 'IT Infrastructure Team', 'Mitigated', 'Deploy centralized patch management across all lab systems.', '2025-08-12', '2026-08-12'),
('RSK-020', 'Outdated antivirus definitions on administrative desktops', 'Several admin office desktops had antivirus signature files over 60 days out of date.', 2, 'Admin Office Desktops', 3, 2, 6, 'Medium', 'IT Infrastructure Team', 'Closed', 'Centralized antivirus management deployed and verified across all desktops.', '2025-07-01', '2026-01-01'),
('RSK-021', 'Unsecured guest Wi-Fi captive portal allowing bypass', 'The guest Wi-Fi captive portal can be bypassed using a simple MAC spoofing technique.', 1, 'Guest Wi-Fi Network', 2, 2, 4, 'Low', 'Network Admin', 'Accepted', 'Residual risk accepted given limited guest network segmentation; monitor for abuse.', '2025-09-18', '2026-09-18'),
('RSK-022', 'Outdated PHP version powering alumni portal', 'The alumni portal runs on an end-of-life PHP version no longer receiving security patches.', 2, 'Alumni Portal', 3, 3, 9, 'Medium', 'Application Security Team', 'Open', 'Upgrade the PHP runtime and all dependent libraries.', '2025-10-22', '2026-08-22'),
('RSK-023', 'No rate-limiting on student login API enabling brute force attempts', 'The login API accepts unlimited authentication attempts with no throttling or lockout.', 2, 'Student Login API', 3, 3, 9, 'Medium', 'Application Security Team', 'Open', 'Implement rate-limiting and CAPTCHA after repeated failed login attempts.', '2025-11-28', '2026-08-28'),
('RSK-024', 'Single server hosting ERP, LMS, and email creating single point of failure', 'All three core services run on one physical server with no redundancy.', 1, 'Primary Application Server', 2, 5, 10, 'High', 'IT Infrastructure Team', 'Open', 'Migrate services to separate virtualized instances with failover.', '2025-12-20', '2026-09-20'),
('RSK-025', 'Transport vendor app collecting student GPS data without explicit consent', 'The outsourced campus transport tracking app collects continuous GPS location without a documented consent flow.', 5, 'Campus Transport Tracking App', 2, 2, 4, 'Low', 'Procurement & Vendor Management', 'Open', 'Review the vendor data processing agreement and implement explicit consent capture.', '2026-01-15', '2026-10-15');

-- ------------------------------------------------------------
-- COMPLIANCE CONTROLS (20)
-- Framework 1 = ISO/IEC 27001:2022 (9 controls)
-- Framework 2 = NIST CSF 2.0 (7 controls)
-- Framework 3 = DPDP Act 2023 (4 controls)
-- ------------------------------------------------------------
INSERT INTO compliance_controls (framework_id, control_ref, control_name, control_description, domain) VALUES
(1, 'A.5.1', 'Policies for information security', 'Information security policy and topic-specific policies shall be defined and approved by management.', 'Organizational'),
(1, 'A.5.7', 'Threat intelligence', 'Information relating to information security threats shall be collected and analyzed.', 'Organizational'),
(1, 'A.5.30', 'ICT readiness for business continuity', 'ICT readiness shall be planned, implemented, and tested based on business continuity objectives.', 'Organizational'),
(1, 'A.6.3', 'Information security awareness, education and training', 'Personnel shall receive appropriate awareness training relevant to their job function.', 'People'),
(1, 'A.8.2', 'Privileged access rights', 'The allocation and use of privileged access rights shall be restricted and managed.', 'Technological'),
(1, 'A.8.9', 'Configuration management', 'Configurations, including security configurations, shall be established, documented, and monitored.', 'Technological'),
(1, 'A.8.16', 'Monitoring activities', 'Networks, systems, and applications shall be monitored for anomalous behavior.', 'Technological'),
(1, 'A.8.24', 'Use of cryptography', 'Rules for the effective use of cryptography, including encryption, shall be defined and implemented.', 'Technological'),
(1, 'A.8.28', 'Secure coding', 'Secure coding principles shall be applied to software development.', 'Technological'),
(2, 'ID.AM-01', 'Hardware inventories', 'Inventories of hardware managed by the organization are maintained.', 'Identify'),
(2, 'PR.AA-01', 'Identity and credential management', 'Identities and credentials for authorized users are managed by the organization.', 'Protect'),
(2, 'PR.DS-01', 'Data-at-rest protection', 'The confidentiality, integrity, and availability of data-at-rest are protected.', 'Protect'),
(2, 'PR.PS-01', 'Configuration management practices', 'Configuration management practices are established and applied.', 'Protect'),
(2, 'DE.CM-01', 'Network monitoring', 'Networks are monitored to detect potential cybersecurity events.', 'Detect'),
(2, 'RS.MA-01', 'Incident response execution', 'The incident response plan is executed once an incident is declared.', 'Respond'),
(2, 'RC.RP-01', 'Recovery plan execution', 'The recovery portion of the incident response plan is executed once initiated.', 'Recover'),
(3, 'DPDP-S8', 'Reasonable security safeguards', 'Data Fiduciaries shall implement reasonable security safeguards to prevent personal data breaches.', 'Data Protection'),
(3, 'DPDP-S5', 'Notice to Data Principals', 'Data Principals shall be given notice describing personal data to be processed and the purpose.', 'Consent Management'),
(3, 'DPDP-S9', 'Processing of children''s data', 'Additional obligations apply when processing personal data of individuals under 18 years of age.', 'Data Protection'),
(3, 'DPDP-S11', 'Right to correction and erasure', 'Data Principals have the right to correction, completion, updating, and erasure of personal data.', 'Data Subject Rights');

-- ------------------------------------------------------------
-- COMPLIANCE STATUS RECORDS (15)
-- Controls 4, 7, 13, 16, and 19 are intentionally left unassessed,
-- to realistically represent controls that haven't been reviewed yet.
-- ------------------------------------------------------------
INSERT INTO compliance_status (control_id, status, evidence, responsible_person, linked_risk_id, last_assessed_date, next_review_date, notes) VALUES
(1, 'Compliant', 'Information Security Policy v2.1 approved by the IT Governance Committee.', 'CISO Office', NULL, '2026-03-01', '2026-09-01', 'Reviewed annually alongside the academic calendar.'),
(2, 'Partially Compliant', 'Subscribed to CERT-In advisories; no formal threat intelligence sharing process exists yet.', 'Network Admin', NULL, '2026-02-15', '2026-08-15', NULL),
(3, 'Non-Compliant', 'No tested disaster recovery plan currently exists for core ICT services.', 'IT Infrastructure Team', 9, '2026-01-20', '2026-07-20', 'Directly tied to open risk RSK-009.'),
(5, 'Partially Compliant', 'Admin roles are defined but not reviewed on a quarterly basis as required.', 'IT Infrastructure Team', 13, '2026-02-01', '2026-08-01', NULL),
(6, 'Non-Compliant', 'Default credentials found active on three core network switches during audit.', 'Network Admin', 5, '2026-01-10', '2026-07-10', NULL),
(8, 'Non-Compliant', 'Student data backups are currently stored without encryption.', 'Data Protection Officer', 11, '2026-02-20', '2026-08-20', NULL),
(9, 'Non-Compliant', 'Fee payment gateway found vulnerable to SQL injection during penetration test.', 'Application Security Team', 1, '2026-03-05', '2026-09-05', 'High-priority remediation tracked via AF-001.'),
(10, 'Compliant', 'Asset register maintained within the ERP IT module, updated monthly.', 'IT Infrastructure Team', NULL, '2026-03-10', '2026-09-10', NULL),
(11, 'Partially Compliant', 'MFA is not yet enforced for faculty administrative accounts.', 'IT Infrastructure Team', 4, '2026-02-25', '2026-08-25', NULL),
(12, 'Non-Compliant', 'Backup encryption at rest has not yet been implemented.', 'Data Protection Officer', 11, '2026-02-20', '2026-08-20', NULL),
(14, 'Partially Compliant', 'Basic firewall logging is enabled; no centralized SIEM correlation in place.', 'Network Admin', NULL, '2026-01-30', '2026-07-30', NULL),
(15, 'Non-Compliant', 'No formal, documented incident response plan exists.', 'IT Infrastructure Team', 10, '2026-01-15', '2026-07-15', 'Surfaced during a simulated ransomware drill, see AF-008.'),
(17, 'Partially Compliant', 'Encryption gaps identified in backup storage during internal review.', 'Data Protection Officer', 11, '2026-03-12', '2026-09-12', NULL),
(18, 'Compliant', 'Privacy notice published on the student portal at the point of admission.', 'Data Protection Officer', NULL, '2026-03-15', '2026-09-15', NULL),
(20, 'Not Applicable', 'Erasure request handling is not yet supported; pending an ERP module update.', 'Data Protection Officer', NULL, '2026-03-18', '2026-09-18', 'Re-assess once the ERP self-service module ships.');

-- ------------------------------------------------------------
-- AUDIT FINDINGS (10)
-- ------------------------------------------------------------
INSERT INTO audit_findings (finding_code, title, description, severity, linked_risk_id, owner, remediation_plan, due_date, status) VALUES
('AF-001', 'SQL injection confirmed in fee payment gateway', 'Penetration test confirmed an exploitable SQL injection vulnerability in the fee payment module.', 'Critical', 1, 'Application Security Team', 'Patch input validation across all payment endpoints and deploy WAF rules.', '2026-07-10', 'Open'),
('AF-002', 'Default vendor credentials still active on two core switches', 'Two core switches were found still using factory-default administrative credentials.', 'High', 5, 'Network Admin', 'Reset credentials and document the new baseline in the configuration registry.', '2026-06-25', 'In Progress'),
('AF-003', 'Faculty admin accounts lack multi-factor authentication', 'None of the sampled faculty admin accounts had MFA enabled.', 'High', 4, 'IT Infrastructure Team', 'Enable TOTP-based MFA for all faculty and admin roles.', '2026-07-05', 'Open'),
('AF-004', 'Server room visitor access not logged', 'No log of visitor entries to the main server room could be produced during the audit.', 'Medium', 8, 'Facilities & Security Team', 'Deploy a biometric access control system with automatic entry logging.', '2026-05-30', 'Overdue'),
('AF-005', 'Unencrypted backup media found in IT storage room', 'Backup drives containing student records were found stored without encryption.', 'High', 11, 'Data Protection Officer', 'Encrypt all backup media and update the backup handling procedure.', '2026-07-20', 'Open'),
('AF-006', 'Outdated antivirus signatures on twelve admin desktops', 'Twelve sampled administrative desktops had antivirus definitions over 60 days out of date.', 'Medium', 20, 'IT Infrastructure Team', 'Push a centralized antivirus update policy to all endpoints.', '2026-04-15', 'Closed'),
('AF-007', 'Canteen vendor app logging unmasked card numbers', 'The outsourced canteen payment app was found writing full, unmasked card numbers to application logs.', 'Critical', 12, 'Procurement & Vendor Management', 'Require vendor remediation and an independent PCI-DSS audit before continued use.', '2026-07-30', 'Open'),
('AF-008', 'No incident response plan during simulated ransomware drill', 'A tabletop ransomware exercise revealed no documented incident response plan was available to staff.', 'High', 10, 'IT Infrastructure Team', 'Draft and formally approve an incident response plan.', '2026-06-15', 'Overdue'),
('AF-009', 'Moodle LMS running plugins with known CVEs', 'Three installed Moodle plugins were confirmed to have publicly disclosed vulnerabilities.', 'Medium', 15, 'Application Security Team', 'Update or remove the affected plugins.', '2026-08-01', 'Open'),
('AF-010', 'Hostel Wi-Fi allows access without authentication', 'Hostel Wi-Fi access points were confirmed to allow connection without any login or encryption.', 'High', 6, 'Network Admin', 'Migrate to WPA2-Enterprise with per-student credential login.', '2026-08-10', 'In Progress');
