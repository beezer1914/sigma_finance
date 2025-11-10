# sigma_finance/routes/reports.py
"""
Reports Blueprint - Financial reporting endpoints

Provides access to financial reports for authorized users
(treasurer, president, vice_president, admin)
"""

from flask import Blueprint, render_template, make_response, flash, redirect, url_for
from flask_login import login_required, current_user
from sigma_finance.utils.decorators import role_required
from sigma_finance.services.reports import (
    get_dues_paid_report,
    get_payment_plan_stats,
    get_dues_summary_stats,
    get_payment_plan_summary,
    export_dues_paid_to_csv,
    export_payment_plans_to_csv,
    get_donation_stats,
    get_donation_monthly_summary,
    get_top_donors,
    get_donation_summary_stats,
    export_donations_to_csv,
    export_top_donors_to_csv
)
from datetime import datetime

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def reports_dashboard():
    """
    Main reports dashboard

    Shows summary statistics for:
    - Dues payments (total, current year, financial status)
    - Payment plans (active, committed, paid, outstanding)

    Access: admin, treasurer, president, vice_president
    """
    try:
        dues_summary = get_dues_summary_stats()
        plan_summary = get_payment_plan_summary()

        return render_template(
            'reports/dashboard.html',
            dues_summary=dues_summary,
            plan_summary=plan_summary
        )
    except Exception as e:
        flash(f"Error loading reports: {str(e)}", "danger")
        return redirect(url_for('dashboard.show_dashboard'))


@reports_bp.route('/dues-paid')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def dues_paid_report():
    """
    Detailed dues paid report

    Shows individual member payment information:
    - Total paid (all time and current year)
    - Payment count and last payment date
    - Financial status

    Access: admin, treasurer, president, vice_president
    """
    try:
        members = get_dues_paid_report()
        summary = get_dues_summary_stats()

        return render_template(
            'reports/dues_paid.html',
            members=members,
            summary=summary
        )
    except Exception as e:
        flash(f"Error loading dues report: {str(e)}", "danger")
        return redirect(url_for('reports.reports_dashboard'))


@reports_bp.route('/payment-plans')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def payment_plans_report():
    """
    Payment plan statistics report

    Shows detailed payment plan progress:
    - Amount paid vs total
    - Balance remaining
    - Percentage complete
    - Number of payments made

    Access: admin, treasurer, president, vice_president
    """
    try:
        plans = get_payment_plan_stats()
        summary = get_payment_plan_summary()

        return render_template(
            'reports/payment_plans.html',
            plans=plans,
            summary=summary
        )
    except Exception as e:
        flash(f"Error loading payment plans report: {str(e)}", "danger")
        return redirect(url_for('reports.reports_dashboard'))


@reports_bp.route('/export/dues-paid')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def export_dues_paid():
    """
    Export dues paid report as CSV

    Downloads a CSV file with all member payment information
    Filename includes current date

    Access: admin, treasurer, president, vice_president
    """
    try:
        csv_data = export_dues_paid_to_csv()

        # Create response with CSV data
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=dues_paid_{datetime.now().strftime("%Y%m%d")}.csv'
        )

        return response
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.dues_paid_report'))


@reports_bp.route('/export/payment-plans')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def export_payment_plans():
    """
    Export payment plans report as CSV

    Downloads a CSV file with all payment plan statistics
    Filename includes current date

    Access: admin, treasurer, president, vice_president
    """
    try:
        csv_data = export_payment_plans_to_csv()

        # Create response with CSV data
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=payment_plans_{datetime.now().strftime("%Y%m%d")}.csv'
        )

        return response
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.payment_plans_report'))


@reports_bp.route('/donations')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def donations_report():
    """
    Donation statistics report

    Shows detailed donation information:
    - Individual donations with tier classification
    - Monthly summary trends
    - Top donors list
    - Member vs non-member breakdown

    Access: admin, treasurer, president, vice_president
    """
    try:
        donations = get_donation_stats()
        summary = get_donation_summary_stats()
        monthly = get_donation_monthly_summary()
        top_donors = get_top_donors(limit=10)

        return render_template(
            'reports/donations.html',
            donations=donations,
            summary=summary,
            monthly=monthly,
            top_donors=top_donors
        )
    except Exception as e:
        flash(f"Error loading donations report: {str(e)}", "danger")
        return redirect(url_for('reports.reports_dashboard'))


@reports_bp.route('/export/donations')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def export_donations():
    """
    Export donations report as CSV

    Downloads a CSV file with all donation information
    Filename includes current date

    Access: admin, treasurer, president, vice_president
    """
    try:
        csv_data = export_donations_to_csv()

        # Create response with CSV data
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=donations_{datetime.now().strftime("%Y%m%d")}.csv'
        )

        return response
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.donations_report'))


@reports_bp.route('/export/top-donors')
@login_required
@role_required('admin', 'treasurer', 'president', 'vice_president')
def export_top_donors():
    """
    Export top donors report as CSV

    Downloads a CSV file with aggregated donor statistics
    Filename includes current date

    Access: admin, treasurer, president, vice_president
    """
    try:
        csv_data = export_top_donors_to_csv()

        # Create response with CSV data
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = (
            f'attachment; filename=top_donors_{datetime.now().strftime("%Y%m%d")}.csv'
        )

        return response
    except Exception as e:
        flash(f"Error exporting report: {str(e)}", "danger")
        return redirect(url_for('reports.donations_report'))
