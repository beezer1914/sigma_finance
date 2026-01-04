# Sigma Finance User Guide

**Version 1.0**
**Last Updated: December 2025**

---

## Table of Contents

### For Members
1. [Getting Started](#getting-started)
   - [Creating Your Account](#creating-your-account)
   - [Logging In](#logging-in)
2. [Making Payments](#making-payments)
   - [One-Time Payment](#one-time-payment)
   - [Setting Up a Payment Plan](#setting-up-a-payment-plan)
3. [Viewing Your Dashboard](#viewing-your-dashboard)

### For Treasurers & Administrators
4. [Managing Members](#managing-members)
   - [Viewing All Members](#viewing-all-members)
   - [Editing Member Details](#editing-member-details)
   - [Creating Invite Codes](#creating-invite-codes)
5. [Financial Reports](#financial-reports)
   - [Viewing Reports](#viewing-reports)
   - [Understanding Financial Status](#understanding-financial-status)
6. [Managing Donations](#managing-donations)

---

# For Members

## Getting Started

### Creating Your Account

To join Sigma Finance, you'll need an invite code from your organization's treasurer.

**Step-by-step:**

1. Navigate to the Sigma Finance website
2. Click the **"Register"** button or go to `/register`

   *[Screenshot: Registration page with empty form]*

3. Fill in the registration form:
   - **Name**: Your full name
   - **Email**: Your email address
   - **Password**: Must be at least 12 characters and include:
     - At least one uppercase letter
     - At least one lowercase letter
     - At least one number
     - At least one special character (!@#$%^&*(),.?":{}|<>)
   - **Invite Code**: The code provided by your treasurer

   *[Screenshot: Registration form filled out with example data]*

4. Click **"Create Account"**
5. You'll be redirected to the login page

**Note:** If you don't have an invite code, contact your organization's treasurer.

---

### Logging In

**Step-by-step:**

1. Go to the Sigma Finance website
2. Click **"Login"** or navigate to `/login`

   *[Screenshot: Login page]*

3. Enter your email and password
4. Click **"Sign In"**
5. You'll be taken to your personal dashboard

**Security Features:**
- After 3 failed login attempts, you'll be locked out for 15 minutes
- This protects your account from unauthorized access

**Forgot Your Password?**
- Click "Forgot Password?" on the login page
- Enter your email address
- Check your email for a password reset link

   *[Screenshot: Forgot password page]*

---

## Making Payments

Sigma Finance offers two ways to make payments: one-time payments and payment plans.

### One-Time Payment

Use this option to make a single payment for dues, fees, or other charges.

**Step-by-step:**

1. Log in to your account
2. From your dashboard, click **"Payments"** in the navigation menu

   *[Screenshot: Dashboard with Payments highlighted]*

3. Click the **"Make a Payment"** button
4. Select **"One-Time Payment"**

   *[Screenshot: Payment type selection]*

5. Enter the payment details:
   - **Amount**: The amount you're paying
   - **Notes** (optional): What this payment is for (e.g., "Semester Dues", "Event Fee")

   *[Screenshot: One-time payment form]*

6. Click **"Proceed to Checkout"**
7. You'll be redirected to Stripe's secure payment page
8. Enter your payment information:
   - Card number
   - Expiration date
   - CVC code
   - Billing zip code

   *[Screenshot: Stripe checkout page]*

9. Click **"Pay"**
10. You'll be redirected back to Sigma Finance with a confirmation

**What Happens Next?**
- Payment is processed immediately
- Your financial status will be updated
- You'll receive a confirmation email
- The payment will appear in your payment history

---

### Setting Up a Payment Plan

Payment plans let you split a larger amount into smaller, regular payments.

**Step-by-step:**

1. Log in to your account
2. Click **"Payment Plans"** in the navigation menu

   *[Screenshot: Dashboard with Payment Plans highlighted]*

3. Click **"Create New Plan"**

   *[Screenshot: Payment Plans page]*

4. Fill in the plan details:
   - **Total Amount**: The total amount you need to pay
   - **Frequency**: How often you want to pay
     - Weekly
     - Bi-weekly (every 2 weeks)
     - Monthly
   - **Start Date**: When you want the plan to begin

   *[Screenshot: Payment plan form with example data]*

5. Review the calculated installment amount
   - The system will show you how much each payment will be
   - Example: $500 total / Monthly = $125 per month for 4 months

6. Click **"Create Payment Plan"**
7. Your plan is now active!

**Managing Your Payment Plan:**

- **View Your Plan**: Go to Payment Plans to see details
- **Make Installment Payments**:
  - Go to the Payments page
  - Click "Make a Payment"
  - Select "Installment Payment"
  - Your current plan balance will be shown
- **Track Progress**: See your remaining balance and payment history

   *[Screenshot: Active payment plan view showing progress]*

**Important Notes:**
- You can only have one active payment plan at a time
- Make payments on time to stay in good standing
- Your financial status will update as you complete payments

---

## Viewing Your Dashboard

Your dashboard shows an overview of your financial status and activity.

**Dashboard Features:**

*[Screenshot: Complete dashboard view]*

1. **Financial Status**: Shows if you're "Financial" or "Not Financial"
2. **Current Balance**: If you have a payment plan, your remaining balance
3. **Recent Payments**: Your last few payments
4. **Quick Actions**: Buttons to make payments or set up plans

**Understanding Your Status:**

- **Financial**: Your dues are paid and you're in good standing
- **Not Financial**: You have outstanding dues or payments
- **Neophyte**: New members exempt from dues during probation

---

# For Treasurers & Administrators

## Managing Members

Treasurers and administrators have additional tools to manage the organization's members and finances.

**Who Has Access?**
- Admin
- Treasurer
- President
- 1st Vice President

---

### Viewing All Members

**Step-by-step:**

1. Log in with your treasurer/admin account
2. Click **"Members"** in the navigation menu

   *[Screenshot: Members page with member list]*

**What You'll See:**

The Members page displays a table with:
- **Name**: Member's full name
- **Role**: Their position in the organization
- **Email**: Contact email
- **Financial Status**: Current dues status
- **Total Paid**: Lifetime payment total
- **Payment Plan**: Whether they have an active plan
- **Plan Balance**: Remaining balance if on a plan

**Filtering Members:**

Use the filter options at the top to find specific members:

*[Screenshot: Filter bar at top of Members page]*

1. **Search**: Type a name or email
2. **Financial Status**: Filter by Financial, Not Financial, or Neophyte
3. **Payment Plan**: Filter by Active Plan or No Plan
4. **Delinquent Button**: Shows members who are not financial AND have no payment plan

**Viewing Member Details:**

Click on any member row to see their complete details:

*[Screenshot: Member detail modal]*

- Full profile information
- Financial summary (total paid, payment count, last payment)
- Active payment plan details
- Recent payment history (last 20 payments)

---

### Editing Member Details

As a treasurer, you can update member information and roles.

**Step-by-step:**

1. Go to the **Members** page
2. Click on the member you want to edit
3. In the member detail modal, click **"Edit Member"** (bottom right)

   *[Screenshot: Member detail modal with Edit Member button highlighted]*

4. The form will appear with editable fields:

   *[Screenshot: Edit member form]*

   - **Name**: Update member's full name
   - **Email**: Change email address
   - **Role**: Assign organizational role:
     - Member
     - President
     - 1st Vice President
     - 2nd Vice President
     - 3rd Vice President
     - Secretary
     - Treasurer
     - Admin
   - **Financial Status**:
     - Financial
     - Not Financial
     - Neophyte
   - **Initiation Date**: Set or update their initiation date
   - **Active Member**: Checkbox to mark if member is active

5. Make your changes
6. Click **"Save Changes"**
7. A success message will appear
8. The member list will automatically refresh

**Important Security Notes:**
- Only authorized roles can edit members
- Email validation prevents duplicate accounts
- All changes are logged for audit purposes

---

### Creating Invite Codes

Invite codes are required for new members to register.

**Step-by-step:**

1. Click **"Invites"** in the navigation menu

   *[Screenshot: Invites page showing existing codes]*

2. Click **"Create Invite"** button

   *[Screenshot: Create invite form]*

3. Fill in the invite details:
   - **Email** (optional): If provided, an invitation email will be sent
   - **Role**: What role the new member will have (usually "Member")
   - **Expiration Date**: When the invite code expires (default: 7 days)

4. Click **"Create Invite Code"**

5. The invite code will be generated and displayed

   *[Screenshot: Success message with new invite code]*

**Invite Code Management:**

View all your invite codes on the Invites page:

- **Code**: The unique invite code
- **Role**: Assigned role for this invite
- **Status**: Available, Used, or Expired
- **Created**: When it was created
- **Expires**: Expiration date
- **Used By**: Who used it (if applicable)

**Statistics:**
- Total Created
- Used
- Available
- Expired

**Deleting Unused Codes:**
- Click the delete icon next to an unused code
- Confirmation will be required
- Cannot delete codes that have been used

---

## Financial Reports

### Viewing Reports

Access comprehensive financial reports and statistics.

**Step-by-step:**

1. Click **"Reports"** in the navigation menu

   *[Screenshot: Reports page with summary statistics]*

**Report Sections:**

**1. Financial Summary**
- Total Collections (all-time)
- Total Payments (count)
- Active Payment Plans (count)
- Average Payment Amount

**2. Member Statistics**
- Total Members
- Financial Members
- Not Financial Members
- Neophytes
- Delinquent Members

**3. Payment Breakdown**
- One-Time Payments (total amount)
- Installment Payments (total amount)
- Donation Payments (total amount)

**4. Recent Activity**
- Latest payments across all members
- Payment method breakdown
- Trends and patterns

*[Screenshot: Reports dashboard showing all statistics]*

---

### Understanding Financial Status

**Financial Status Definitions:**

**Financial**
- Member has paid all current dues
- In good standing with the organization
- Badge color: Green

**Not Financial**
- Member has outstanding dues
- May have restrictions on activities
- Badge color: Red

**Neophyte**
- New member during probation period
- Exempt from dues until initiated
- Automatically set based on initiation date
- Badge color: Blue

**Delinquent**
- Not financial AND no active payment plan
- Requires immediate attention
- Highlighted in red on Members page

**How Status is Determined:**
- Neophytes: Initiated less than one semester ago (based on initiation_date)
- Financial: Set manually by treasurer based on payments
- Payment plans affect financial standing

---

## Managing Donations

Track and manage one-time donations to the organization.

**Step-by-step:**

1. Click **"Donations"** in the navigation menu

   *[Screenshot: Donations page]*

2. View donation statistics:
   - Total Donations (amount)
   - Number of Donations
   - Average Donation Amount
   - Top Donors

**Recording a Donation:**

1. Click **"Record Donation"**

   *[Screenshot: Record donation form]*

2. Fill in donation details:
   - **Donor Name**: Who made the donation
   - **Email** (optional): Donor's email
   - **Amount**: Donation amount
   - **Payment Method**: Cash, Check, Card, etc.
   - **Notes** (optional): Purpose or description

3. Click **"Record Donation"**
4. Donation will appear in the list

**Donation List Features:**
- Filter by date range
- Search by donor name
- Sort by amount or date
- Export to CSV (if available)

*[Screenshot: Donations list with multiple entries]*

---

## Treasurer Dashboard

Your treasurer dashboard provides quick access to critical information.

**Dashboard Sections:**

*[Screenshot: Treasurer dashboard overview]*

1. **Key Metrics**
   - Total Collections This Month
   - Active Members
   - Pending Payment Plans
   - Delinquent Members Count

2. **Quick Actions**
   - Create Invite Code
   - View Members
   - Access Reports
   - Record Donation

3. **Recent Activity Feed**
   - Latest payments
   - New registrations
   - Payment plan creations

4. **Alerts & Notifications**
   - Expiring invite codes
   - Delinquent member count
   - Failed payment attempts

---

## Frequently Asked Questions

### For Members

**Q: I forgot my password. How do I reset it?**
A: Click "Forgot Password" on the login page, enter your email, and follow the reset link sent to you.

**Q: Why can't I log in after 3 attempts?**
A: For security, accounts are temporarily locked after 3 failed login attempts. Wait 15 minutes and try again.

**Q: Can I change my payment plan after creating it?**
A: Contact your treasurer to modify or cancel your payment plan.

**Q: When will my financial status update after payment?**
A: Payment status updates immediately, but financial status is updated by the treasurer.

### For Treasurers

**Q: How do I make someone a treasurer?**
A: Edit their member details and change their role to "Treasurer".

**Q: Can members edit their own information?**
A: No, only treasurers and admins can edit member details for security.

**Q: What happens to expired invite codes?**
A: They can no longer be used for registration but remain in the system for record-keeping.

**Q: How do I export financial data?**
A: Use the Reports page to view data. Contact your admin for export functionality.

---

## Support & Contact

For technical issues or questions:
- Contact your organization's treasurer
- Email: [treasurer email]
- For system issues: [admin email]

---

## Security & Privacy

**Account Security:**
- Passwords must be strong (12+ characters with mixed case, numbers, symbols)
- Sessions expire after inactivity
- Failed login attempts are limited

**Data Privacy:**
- Financial information is encrypted
- Payment processing through Stripe (PCI compliant)
- Only authorized roles can view member details

**Best Practices:**
- Never share your password
- Log out after using shared computers
- Report suspicious activity immediately

---

**End of User Guide**

*For technical documentation or development information, see README.md*
