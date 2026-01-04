# import_historical_payments.py
"""
Import historical payments from Excel file
Usage: python import_historical_payments.py

This script:
1. Reads the Excel file with 2024-2025 payment data
2. Matches members by name or email (if available)
3. Creates payment records for matched users only
4. Skips users who haven't registered yet
"""

import pandas as pd
from datetime import datetime
from sigma_finance.app import create_app
from sigma_finance.extensions import db
from sigma_finance.models import User, Payment

def clean_name(name):
    """Clean and normalize names for matching"""
    if pd.isna(name):
        return ""
    return str(name).strip().lower()

def find_user_by_name(first_name, last_name, email=None):
    """
    Try to find a user by name or email
    Returns User object or None
    """
    first_clean = clean_name(first_name)
    last_clean = clean_name(last_name)
    
    # Try exact name match first
    full_name = f"{first_clean} {last_clean}"
    user = User.query.filter(
        db.func.lower(User.name) == full_name
    ).first()
    
    if user:
        return user
    
    # Try email match if email provided
    if email and pd.notna(email) and str(email).strip():
        email_clean = str(email).strip().lower()
        user = User.query.filter(
            db.func.lower(User.email) == email_clean
        ).first()
        if user:
            return user
    
    # Try partial name match (first and last name in any order)
    users = User.query.all()
    for user in users:
        user_name_lower = user.name.lower()
        if first_clean in user_name_lower and last_clean in user_name_lower:
            return user
    
    return None

def import_payments(excel_file, dry_run=True):
    """
    Import payments from Excel file
    
    Args:
        excel_file: Path to Excel file
        dry_run: If True, only show what would be imported without saving
    """
    
    # Read Excel file
    df = pd.read_excel(excel_file, sheet_name='Chapter Dues 2025-2026')
    
    print(f"\n{'='*60}")
    print(f"📊 HISTORICAL PAYMENT IMPORT")
    print(f"{'='*60}")
    print(f"Total records in Excel: {len(df)}")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE IMPORT'}")
    print(f"{'='*60}\n")
    
    stats = {
        'total': len(df),
        'matched': 0,
        'not_matched': 0,
        'imported': 0,
        'skipped_no_payment': 0,
        'errors': 0
    }
    
    not_matched_users = []
    
    for index, row in df.iterrows():
        first_name = row.get('First Name', '')
        last_name = row.get('Last Name', '')
        email = row.get('Email', None)
        total_paid = row.get('Total Paid', 0)
        q1_amount = row.get('Q1 Amount', 0)
        q2_amount = row.get('Q2 Amount', 0)
        
        # Skip rows with missing names (summary rows, totals, etc.)
        if pd.isna(first_name) or pd.isna(last_name):
            stats['skipped_no_payment'] += 1
            continue
        
        # Skip summary rows like "Quarter Total", "Addt'l Deposit", etc.
        if str(first_name).strip() in ['Quarter Total', 'Addt\'l Deposit', 'Percent', '']:
            stats['skipped_no_payment'] += 1
            continue
        
        # Clean values
        if pd.isna(total_paid):
            total_paid = 0
        if pd.isna(q1_amount):
            q1_amount = 0
        if pd.isna(q2_amount):
            q2_amount = 0
            
        total_paid = float(total_paid)
        q1_amount = float(q1_amount)
        q2_amount = float(q2_amount)
        
        # Skip if no payment
        if total_paid == 0:
            stats['skipped_no_payment'] += 1
            continue
        
        # Try to find matching user
        user = find_user_by_name(first_name, last_name, email)
        
        if user:
            stats['matched'] += 1
            print(f"✅ MATCH: {first_name} {last_name} → {user.name} (${total_paid})")
            
            try:
                # Create Q1 payment if amount > 0
                if q1_amount > 0:
                    q1_payment = Payment(
                        user_id=user.id,
                        amount=q1_amount,
                        date=datetime(2024, 9, 1),  # Q1 2024 (adjust as needed)
                        method='historical',
                        payment_type='one-time',
                        notes='Historical Q1 2024-2025 payment (imported)'
                    )
                    if not dry_run:
                        db.session.add(q1_payment)
                    print(f"   💰 Q1: ${q1_amount}")
                
                # Create Q2 payment if amount > 0
                if q2_amount > 0:
                    q2_payment = Payment(
                        user_id=user.id,
                        amount=q2_amount,
                        date=datetime(2025, 1, 1),  # Q2 2025 (adjust as needed)
                        method='historical',
                        payment_type='one-time',
                        notes='Historical Q2 2024-2025 payment (imported)'
                    )
                    if not dry_run:
                        db.session.add(q2_payment)
                    print(f"   💰 Q2: ${q2_amount}")
                
                # If only total is available (no Q1/Q2 breakdown)
                if total_paid > 0 and q1_amount == 0 and q2_amount == 0:
                    payment = Payment(
                        user_id=user.id,
                        amount=total_paid,
                        date=datetime(2024, 9, 1),  # Default date
                        method='historical',
                        payment_type='one-time',
                        notes='Historical 2024-2025 payment (imported)'
                    )
                    if not dry_run:
                        db.session.add(payment)
                    print(f"   💰 Total: ${total_paid}")
                
                stats['imported'] += 1
                
            except Exception as e:
                stats['errors'] += 1
                print(f"   ❌ ERROR: {str(e)}")
        else:
            stats['not_matched'] += 1
            not_matched_users.append({
                'name': f"{first_name} {last_name}",
                'email': email if pd.notna(email) else 'N/A',
                'amount': total_paid
            })
            print(f"⚠️  NOT FOUND: {first_name} {last_name} (${total_paid})")
    
    # Commit if not dry run
    if not dry_run:
        try:
            db.session.commit()
            print(f"\n✅ Changes committed to database!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR committing to database: {str(e)}")
            return
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 IMPORT SUMMARY")
    print(f"{'='*60}")
    print(f"Total records:           {stats['total']}")
    print(f"✅ Matched users:        {stats['matched']}")
    print(f"💰 Payments imported:    {stats['imported']}")
    print(f"⚠️  Not matched:          {stats['not_matched']}")
    print(f"⏭️  Skipped (no payment): {stats['skipped_no_payment']}")
    print(f"❌ Errors:               {stats['errors']}")
    print(f"{'='*60}\n")
    
    # Show users not matched
    if not_matched_users:
        print(f"\n⚠️  USERS NOT FOUND IN APP ({len(not_matched_users)}):")
        print(f"{'='*60}")
        for u in not_matched_users:
            print(f"  • {u['name']} ({u['email']}) - ${u['amount']}")
        print(f"\nThese users need to register in the app before their")
        print(f"historical payments can be imported.\n")
    
    if dry_run:
        print(f"\n🔍 This was a DRY RUN - no changes were made.")
        print(f"Run with dry_run=False to actually import the data.\n")

def main():
    """Main function"""
    app = create_app()
    
    with app.app_context():
        excel_file = 'Chapter 2025 Dues (1).xlsx'
        
        # First do a dry run to see what will happen
        print("Running DRY RUN first...\n")
        import_payments(excel_file, dry_run=True)
        
        # Ask for confirmation
        response = input("\n🚨 Do you want to proceed with the actual import? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            print("\n🚀 Starting actual import...\n")
            import_payments(excel_file, dry_run=False)
            print("\n✅ Import complete!")
        else:
            print("\n❌ Import cancelled.")

if __name__ == "__main__":
    main()