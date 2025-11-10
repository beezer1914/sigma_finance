# sigma_finance/services/reports.py
"""
Report generation and data aggregation services

This module provides functions for generating financial reports
from database views. All functions are cached for performance.
"""

from sigma_finance.models import (
    DuesPaidView,
    PaymentPlanStatsView,
    DonationStatsView,
    DonationMonthlySummary,
    TopDonorsView
)
from sigma_finance.extensions import db, cache
from io import BytesIO
from datetime import datetime


# ============================================================================
# CACHED REPORT DATA FUNCTIONS
# ============================================================================

@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_dues_paid_report():
    """
    Get comprehensive dues paid report for all active members

    Returns:
        list: List of DuesPaidView objects with payment information

    Cached: 10 minutes
    """
    return DuesPaidView.query.all()


@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_payment_plan_stats():
    """
    Get payment plan statistics for all plans

    Returns:
        list: List of PaymentPlanStatsView objects with plan progress

    Cached: 10 minutes
    """
    return PaymentPlanStatsView.query.all()


# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

def get_dues_summary_stats():
    """
    Calculate summary statistics for dues payments

    Returns:
        dict: Summary statistics including:
            - total_members: Total active members
            - financial_members: Members who are financial
            - not_financial: Members who are not financial
            - total_collected_all_time: Total ever collected
            - total_collected_this_year: Total for current dues year
            - average_paid: Average amount paid per member
    """
    data = get_dues_paid_report()

    if not data:
        return {
            'total_members': 0,
            'financial_members': 0,
            'not_financial': 0,
            'total_collected_all_time': 0,
            'total_collected_this_year': 0,
            'average_paid': 0
        }

    return {
        'total_members': len(data),
        'financial_members': sum(
            1 for m in data
            if m.financial_status in ['financial', 'neophyte']
        ),
        'not_financial': sum(
            1 for m in data
            if m.financial_status == 'not financial'
        ),
        'total_collected_all_time': float(sum(m.total_paid for m in data)),
        'total_collected_this_year': float(sum(m.current_year_paid for m in data)),
        'average_paid': float(sum(m.total_paid for m in data) / len(data))
    }


def get_payment_plan_summary():
    """
    Calculate summary statistics for payment plans

    Returns:
        dict: Summary statistics including:
            - total_active_plans: Number of active plans
            - total_committed: Total amount committed in active plans
            - total_paid_on_plans: Total amount paid on active plans
            - total_outstanding: Total balance remaining
            - average_completion: Average completion percentage
    """
    data = get_payment_plan_stats()
    active_plans = [p for p in data if p.status and p.status.lower() == 'active']

    if not active_plans:
        return {
            'total_active_plans': 0,
            'total_committed': 0,
            'total_paid_on_plans': 0,
            'total_outstanding': 0,
            'average_completion': 0
        }

    return {
        'total_active_plans': len(active_plans),
        'total_committed': float(sum(p.total_amount for p in active_plans)),
        'total_paid_on_plans': float(sum(p.amount_paid for p in active_plans)),
        'total_outstanding': float(sum(p.balance_remaining for p in active_plans)),
        'average_completion': float(
            sum(p.percent_complete for p in active_plans) / len(active_plans)
        )
    }


# ============================================================================
# CSV EXPORT FUNCTIONS
# ============================================================================

def export_dues_paid_to_csv():
    """
    Export dues paid report to CSV format

    Returns:
        bytes: UTF-8 encoded CSV data with BOM for Excel compatibility

    CSV Columns:
        Name, Email, Role, Financial Status, Initiation Date,
        Total Paid (All Time), Current Year Paid, Payment Count, Last Payment
    """
    import csv
    from io import StringIO

    data = get_dues_paid_report()

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Name',
        'Email',
        'Role',
        'Financial Status',
        'Initiation Date',
        'Total Paid (All Time)',
        'Current Year Paid',
        'Payment Count',
        'Last Payment'
    ])

    # Data rows
    for member in data:
        writer.writerow([
            member.name,
            member.email,
            member.role,
            member.financial_status,
            member.initiation_date.strftime('%Y-%m-%d') if member.initiation_date else '',
            f"${float(member.total_paid):.2f}",
            f"${float(member.current_year_paid):.2f}",
            member.payment_count,
            member.last_payment_date.strftime('%Y-%m-%d') if member.last_payment_date else ''
        ])

    # Convert to bytes with UTF-8 BOM for Excel
    csv_string = output.getvalue()
    return '\ufeff' + csv_string  # Add BOM


def export_payment_plans_to_csv():
    """
    Export payment plan statistics to CSV format

    Returns:
        bytes: UTF-8 encoded CSV data with BOM for Excel compatibility

    CSV Columns:
        Name, Email, Frequency, Start Date, End Date, Total Amount,
        Installment, Status, Expected Installments, Payments Made,
        Amount Paid, Balance Remaining, % Complete
    """
    import csv
    from io import StringIO

    data = get_payment_plan_stats()

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Name',
        'Email',
        'Frequency',
        'Start Date',
        'End Date',
        'Total Amount',
        'Installment',
        'Status',
        'Expected Installments',
        'Payments Made',
        'Amount Paid',
        'Balance Remaining',
        '% Complete'
    ])

    # Data rows
    for plan in data:
        writer.writerow([
            plan.name,
            plan.email,
            plan.frequency,
            plan.start_date.strftime('%Y-%m-%d'),
            plan.end_date.strftime('%Y-%m-%d'),
            f"${float(plan.total_amount):.2f}",
            f"${float(plan.installment_amount):.2f}",
            plan.status,
            plan.expected_installments,
            plan.payments_made,
            f"${float(plan.amount_paid):.2f}",
            f"${float(plan.balance_remaining):.2f}",
            f"{float(plan.percent_complete):.1f}%"
        ])

    # Convert to string with UTF-8 BOM for Excel
    csv_string = output.getvalue()
    return '\ufeff' + csv_string  # Add BOM


# ============================================================================
# CACHE INVALIDATION
# ============================================================================

def invalidate_reports_cache():
    """
    Clear all report caches when data changes

    Call this function after:
    - Creating or updating payments
    - Creating or updating payment plans
    - Changing user financial status
    - Creating or updating donations
    """
    cache.delete_memoized(get_dues_paid_report)
    cache.delete_memoized(get_payment_plan_stats)
    cache.delete_memoized(get_donation_stats)
    cache.delete_memoized(get_donation_monthly_summary)
    cache.delete_memoized(get_top_donors)


# ============================================================================
# DONATION REPORT FUNCTIONS
# ============================================================================

@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_donation_stats():
    """
    Get comprehensive donation statistics

    Returns:
        list: List of DonationStatsView objects with donation information

    Cached: 10 minutes
    """
    return DonationStatsView.query.all()


@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_donation_monthly_summary():
    """
    Get monthly donation summary statistics

    Returns:
        list: List of DonationMonthlySummary objects with monthly totals

    Cached: 10 minutes
    """
    return DonationMonthlySummary.query.all()


@cache.memoize(timeout=600)  # Cache for 10 minutes
def get_top_donors(limit=None):
    """
    Get top donors list

    Args:
        limit: Optional limit for number of donors to return

    Returns:
        list: List of TopDonorsView objects sorted by total donated

    Cached: 10 minutes
    """
    query = TopDonorsView.query
    if limit:
        query = query.limit(limit)
    return query.all()


def get_donation_summary_stats():
    """
    Calculate summary statistics for donations

    Returns:
        dict: Summary statistics including:
            - total_donations: Total number of donations
            - unique_donors: Number of unique donors
            - total_amount: Total amount donated
            - avg_donation: Average donation amount
            - member_donations: Number from members
            - non_member_donations: Number from non-members
            - member_amount: Total from members
            - non_member_amount: Total from non-members
    """
    data = get_donation_stats()

    if not data:
        return {
            'total_donations': 0,
            'unique_donors': 0,
            'total_amount': 0,
            'avg_donation': 0,
            'member_donations': 0,
            'non_member_donations': 0,
            'member_amount': 0,
            'non_member_amount': 0
        }

    unique_emails = set(d.donor_email for d in data)
    member_donations = [d for d in data if d.donor_type == 'Member']
    non_member_donations = [d for d in data if d.donor_type == 'Non-Member']

    return {
        'total_donations': len(data),
        'unique_donors': len(unique_emails),
        'total_amount': float(sum(d.amount for d in data)),
        'avg_donation': float(sum(d.amount for d in data) / len(data)),
        'member_donations': len(member_donations),
        'non_member_donations': len(non_member_donations),
        'member_amount': float(sum(d.amount for d in member_donations)),
        'non_member_amount': float(sum(d.amount for d in non_member_donations))
    }


def export_donations_to_csv():
    """
    Export donation statistics to CSV format

    Returns:
        str: UTF-8 encoded CSV data with BOM for Excel compatibility

    CSV Columns:
        Donor Name, Email, Amount, Date, Method, Tier, Donor Type,
        Member Name (if applicable), Anonymous
    """
    import csv
    from io import StringIO

    data = get_donation_stats()

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Donor Name',
        'Email',
        'Amount',
        'Date',
        'Method',
        'Donation Tier',
        'Donor Type',
        'Member Name',
        'Anonymous',
        'Notes'
    ])

    # Data rows
    for donation in data:
        writer.writerow([
            donation.donor_name if not donation.anonymous else 'Anonymous',
            donation.donor_email if not donation.anonymous else 'Hidden',
            f"${float(donation.amount):.2f}",
            donation.date.strftime('%Y-%m-%d %I:%M %p') if donation.date else '',
            donation.method or '',
            donation.donation_tier or '',
            donation.donor_type or '',
            donation.member_name or '',
            'Yes' if donation.anonymous else 'No',
            donation.notes or ''
        ])

    # Convert to string with UTF-8 BOM for Excel
    csv_string = output.getvalue()
    return '\ufeff' + csv_string  # Add BOM


def export_top_donors_to_csv():
    """
    Export top donors report to CSV format

    Returns:
        str: UTF-8 encoded CSV data with BOM for Excel compatibility

    CSV Columns:
        Donor Name, Email, Total Donated, Donation Count, Avg Donation,
        Donor Level, First Donation, Last Donation
    """
    import csv
    from io import StringIO

    data = get_top_donors()

    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        'Donor Name',
        'Email',
        'Total Donated',
        'Donation Count',
        'Avg Donation',
        'Donor Level',
        'Member Name',
        'First Donation',
        'Last Donation'
    ])

    # Data rows
    for donor in data:
        writer.writerow([
            donor.donor_name if not donor.has_anonymous_donations else f"{donor.donor_name} *",
            donor.donor_email,
            f"${float(donor.total_donated):.2f}",
            donor.donation_count,
            f"${float(donor.avg_donation):.2f}",
            donor.donor_level or '',
            donor.member_name or '',
            donor.first_donation_date.strftime('%Y-%m-%d') if donor.first_donation_date else '',
            donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else ''
        ])

    # Convert to string with UTF-8 BOM for Excel
    csv_string = output.getvalue()
    return '\ufeff' + csv_string  # Add BOM
