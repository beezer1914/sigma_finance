-- ================================================================
-- Sigma Finance - Donation Views for Local SQLite Development
-- ================================================================
-- Run this file in DB Browser for SQLite or via sqlite3 CLI
-- This should be run AFTER you run the donation table migration
-- ================================================================

-- ================================================================
-- VIEW: Donation Statistics View
-- Purpose: Shows comprehensive donation information with summaries
-- ================================================================
DROP VIEW IF EXISTS donation_stats_view;
CREATE VIEW donation_stats_view AS
SELECT
    d.id as donation_id,
    d.donor_name,
    d.donor_email,
    d.amount,
    d.date,
    d.method,
    d.anonymous,
    d.notes,

    -- Link to user if donor is a member
    d.user_id,
    u.name as member_name,
    u.role as member_role,
    u.financial_status,

    -- Date grouping helpers for reports (SQLite uses different functions)
    strftime('%Y-%m', d.date) as donation_month,
    strftime('%Y', d.date) as donation_year,
    CAST(strftime('%Y', d.date) AS INTEGER) as year,
    CAST(strftime('%m', d.date) AS INTEGER) as month,

    -- Categorize by amount range (useful for reporting)
    CASE
        WHEN d.amount < 25 THEN 'Small ($0-$24)'
        WHEN d.amount < 50 THEN 'Medium ($25-$49)'
        WHEN d.amount < 100 THEN 'Large ($50-$99)'
        WHEN d.amount < 250 THEN 'Major ($100-$249)'
        ELSE 'Premium ($250+)'
    END as donation_tier,

    -- Flag for member vs non-member donations
    CASE
        WHEN d.user_id IS NOT NULL THEN 'Member'
        ELSE 'Non-Member'
    END as donor_type

FROM donation d
LEFT JOIN user u ON d.user_id = u.id
ORDER BY d.date DESC;


-- ================================================================
-- VIEW: Donation Summary by Month
-- Purpose: Monthly donation totals and counts
-- ================================================================
DROP VIEW IF EXISTS donation_monthly_summary;
CREATE VIEW donation_monthly_summary AS
SELECT
    -- Return first day of month as a proper datetime string that SQLAlchemy can parse
    date(strftime('%Y-%m', d.date) || '-01') as month,
    CAST(strftime('%Y', d.date) AS INTEGER) as year,
    CAST(strftime('%m', d.date) AS INTEGER) as month_num,
    strftime('%Y-%m', d.date) as month_name,  -- SQLite doesn't have TO_CHAR, we'll format in Python

    COUNT(*) as donation_count,
    COUNT(DISTINCT d.donor_email) as unique_donors,
    SUM(d.amount) as total_amount,
    AVG(d.amount) as avg_amount,
    MIN(d.amount) as min_amount,
    MAX(d.amount) as max_amount,

    -- Member vs non-member breakdown
    SUM(CASE WHEN d.user_id IS NOT NULL THEN 1 ELSE 0 END) as member_donations,
    SUM(CASE WHEN d.user_id IS NULL THEN 1 ELSE 0 END) as non_member_donations,
    SUM(CASE WHEN d.user_id IS NOT NULL THEN d.amount ELSE 0 END) as member_amount,
    SUM(CASE WHEN d.user_id IS NULL THEN d.amount ELSE 0 END) as non_member_amount

FROM donation d
GROUP BY strftime('%Y-%m', d.date)
ORDER BY month DESC;


-- ================================================================
-- VIEW: Top Donors
-- Purpose: Aggregate donations by donor for recognition/reporting
-- ================================================================
DROP VIEW IF EXISTS top_donors_view;
CREATE VIEW top_donors_view AS
SELECT
    d.donor_email,
    MAX(d.donor_name) as donor_name,
    d.user_id,
    MAX(u.name) as member_name,

    COUNT(*) as donation_count,
    SUM(d.amount) as total_donated,
    AVG(d.amount) as avg_donation,
    MIN(d.date) as first_donation_date,
    MAX(d.date) as last_donation_date,

    -- Check if any donations are marked anonymous (SQLite uses MAX instead of BOOL_OR)
    MAX(CASE WHEN d.anonymous = 1 THEN 1 ELSE 0 END) as has_anonymous_donations,

    -- Categorize donor level
    CASE
        WHEN SUM(d.amount) < 50 THEN 'Friend'
        WHEN SUM(d.amount) < 100 THEN 'Supporter'
        WHEN SUM(d.amount) < 250 THEN 'Patron'
        WHEN SUM(d.amount) < 500 THEN 'Benefactor'
        ELSE 'Champion'
    END as donor_level

FROM donation d
LEFT JOIN user u ON d.user_id = u.id
GROUP BY d.donor_email, d.user_id
ORDER BY total_donated DESC;


-- ================================================================
-- Test Queries
-- ================================================================

-- Test 1: View all donation statistics
-- SELECT * FROM donation_stats_view LIMIT 10;

-- Test 2: Monthly summary
-- SELECT * FROM donation_monthly_summary;

-- Test 3: Top donors
-- SELECT * FROM top_donors_view LIMIT 20;

-- Test 4: Overall donation statistics
-- SELECT
--     COUNT(*) as total_donations,
--     COUNT(DISTINCT donor_email) as unique_donors,
--     SUM(amount) as total_amount,
--     AVG(amount) as avg_donation,
--     MAX(amount) as largest_donation,
--     MIN(amount) as smallest_donation
-- FROM donation_stats_view;

-- Test 5: Donations by tier
-- SELECT
--     donation_tier,
--     COUNT(*) as count,
--     SUM(amount) as total
-- FROM donation_stats_view
-- GROUP BY donation_tier
-- ORDER BY
--     CASE donation_tier
--         WHEN 'Small ($0-$24)' THEN 1
--         WHEN 'Medium ($25-$49)' THEN 2
--         WHEN 'Large ($50-$99)' THEN 3
--         WHEN 'Major ($100-$249)' THEN 4
--         WHEN 'Premium ($250+)' THEN 5
--     END;

-- Test 6: Member vs Non-Member donations
-- SELECT
--     donor_type,
--     COUNT(*) as count,
--     SUM(amount) as total,
--     AVG(amount) as average
-- FROM donation_stats_view
-- GROUP BY donor_type;
