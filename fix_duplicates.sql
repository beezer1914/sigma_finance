-- ============================================================
-- Fix Duplicate Historical Payments in PostgreSQL
-- ============================================================
--
-- This script identifies and removes duplicate historical payments
-- that were imported twice from the Excel file.
--
-- USAGE:
-- 1. First run the SELECT queries to verify what will be deleted
-- 2. Then run the DELETE query if everything looks correct
-- 3. Finally verify the results
--
-- ============================================================

-- STEP 1: Check how many historical payments exist
-- ============================================================
SELECT COUNT(*) as total_historical_payments
FROM payment
WHERE method = 'historical';

-- STEP 2: Find duplicate payments (same user, date, and amount)
-- ============================================================
SELECT
    user_id,
    date::date as payment_date,
    amount,
    COUNT(*) as duplicate_count,
    ARRAY_AGG(id ORDER BY id) as payment_ids,
    ARRAY_AGG(notes ORDER BY id) as notes_list
FROM payment
WHERE method = 'historical'
GROUP BY user_id, date::date, amount
HAVING COUNT(*) > 1
ORDER BY user_id, date::date;

-- STEP 3: See detailed information about duplicates
-- ============================================================
WITH duplicates AS (
    SELECT
        user_id,
        date::date as payment_date,
        amount,
        COUNT(*) as dup_count
    FROM payment
    WHERE method = 'historical'
    GROUP BY user_id, date::date, amount
    HAVING COUNT(*) > 1
)
SELECT
    u.name as user_name,
    u.email,
    p.id as payment_id,
    p.date,
    p.amount,
    p.notes,
    p.created_at
FROM payment p
JOIN "user" u ON p.user_id = u.id
WHERE p.method = 'historical'
AND (p.user_id, p.date::date, p.amount) IN (
    SELECT user_id, payment_date, amount FROM duplicates
)
ORDER BY u.name, p.date, p.id;

-- STEP 4: DELETE DUPLICATES (keeping oldest, deleting newer ones)
-- ============================================================
-- ⚠️ WARNING: This will permanently delete duplicate payments!
-- ⚠️ Make sure to backup your database first!
-- ⚠️ Run the SELECT queries above first to verify!
--
-- Uncomment the DELETE statement below when ready to execute:

/*
DELETE FROM payment
WHERE id IN (
    SELECT p2.id
    FROM payment p1
    JOIN payment p2 ON
        p1.user_id = p2.user_id
        AND p1.date::date = p2.date::date
        AND p1.amount = p2.amount
        AND p1.method = 'historical'
        AND p2.method = 'historical'
        AND p1.id < p2.id  -- Keep the oldest (lower ID), delete the newer one
);
*/

-- STEP 5: After deletion, verify the duplicates are gone
-- ============================================================
SELECT
    user_id,
    date::date as payment_date,
    amount,
    COUNT(*) as count
FROM payment
WHERE method = 'historical'
GROUP BY user_id, date::date, amount
HAVING COUNT(*) > 1;

-- Should return 0 rows if duplicates are successfully removed

-- STEP 6: Check total amounts per user after cleanup
-- ============================================================
SELECT
    u.name,
    u.email,
    COUNT(p.id) as payment_count,
    SUM(p.amount) as total_paid
FROM "user" u
LEFT JOIN payment p ON u.id = p.user_id
GROUP BY u.id, u.name, u.email
ORDER BY u.name;
