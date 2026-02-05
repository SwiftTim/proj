# Quick Start: PDF Push & Compare Feature

## What is it?
The **PDF Push & Compare** feature allows you to verify the integrity of county budget reports by comparing them against the official Controller of Budget Implementation Review Report (CBIRR).

## How to Use

### Step 1: Prerequisites
1. **Upload the Official CBIRR PDF**
   - Go to Dashboard → Upload tab
   - Upload the file named "CGBIRR August 2025.pdf"
   - This serves as the official reference document

2. **Upload County Budget PDFs**
   - Upload any county budget documents you want to verify
   - These will be the "pushed" documents for comparison

3. **Sign In**
   - The comparison feature requires authentication
   - Click "Sign In" and create an account

### Step 2: Run a Comparison
1. Navigate to **Dashboard → Compare** tab
2. Select **"PDF Push & Compare"** mode (default)
3. Choose your **target county** from the dropdown
4. Select the **merits** you want to compare:
   - ✅ **Absorption Gap**: Development spending vs target
   - ✅ **Revenue Variance**: Projected vs actual revenue
   - ✅ **Wage Bill Compliance**: Personnel costs vs 35% limit
   - ✅ **Debt Stock**: Pending bills comparison
5. Click **"Trigger Integrity Cross-Reference"**

### Step 3: Review Results
The system will display a **Budget Integrity Scorecard** showing:

#### 📊 Integrity Score (0-100)
- **Green (>70)**: High integrity - data matches well
- **Yellow (40-70)**: Moderate concerns - some discrepancies
- **Red (<40)**: Significant issues - major discrepancies found

#### ⚖️ Executive Verdict
AI-generated summary of the integrity assessment

#### 🚨 Integrity Alerts
Specific warnings about data discrepancies:
- Underreporting (county claims lower debt than official)
- Overreporting (county claims higher revenue than official)
- Missing data points

#### 📈 Merit Comparisons
For each selected merit, you'll see:
- **Official CBIRR Value** with source citation
- **Pushed Document Value** with source citation
- **Variance Percentage** (color-coded)
- **Detailed Explanation** of any discrepancies
- **Status**: ✓ Verified, ⚠ Missing Data, or 🚨 Alert

## Example Use Cases

### Use Case 1: Verify Nairobi's Debt Reporting
**Scenario**: You want to check if Nairobi County is accurately reporting their pending bills.

**Steps**:
1. Select County: "Nairobi"
2. Select Merit: "Debt Stock"
3. Run comparison
4. **Expected Result**: 
   - Official: Ksh 86.77B (from CBIRR Section 3.1.14)
   - If county reports significantly less, you'll get an integrity alert

### Use Case 2: Check Revenue Collection Accuracy
**Scenario**: Verify if a county's own-source revenue claims match official records.

**Steps**:
1. Select County: "Embu"
2. Select Merit: "Revenue Variance"
3. Run comparison
4. **Expected Result**:
   - Official OSR Target: ~Ksh 371M
   - Official OSR Actual: [from CBIRR Section 3.X.2]
   - Variance calculation and integrity assessment

### Use Case 3: Multi-Merit Audit
**Scenario**: Comprehensive integrity check across all financial indicators.

**Steps**:
1. Select County: Any county
2. Select ALL merits (Absorption Gap, Revenue Variance, Wage Bill, Debt Stock)
3. Run comparison
4. **Expected Result**:
   - Overall integrity score
   - Multiple comparison cards
   - Comprehensive verdict

## Understanding the Results

### Integrity Score Breakdown
```
100 points = Perfect match
-15 points = Major discrepancy (>10% variance)
-5 points  = Minor discrepancy (5-10% variance)
-25 points = Missing data point
```

### Status Indicators
- ✅ **Verified**: Values match within ±5%
- ⚠️ **Data Missing**: Figure not found in one or both documents
- 🚨 **Alert**: Significant discrepancy detected

### Variance Color Coding
- 🟢 **Green** (<5%): Acceptable variance
- 🟡 **Yellow** (5-10%): Minor concern
- 🔴 **Red** (>10%): Major discrepancy

## Troubleshooting

### "Official CBIRR reference PDF not found"
**Solution**: Upload the CBIRR PDF to `public/uploads/` with the exact name "CGBIRR August 2025.pdf"

### "No uploaded documents found for this county"
**Solution**: Upload a budget document for the selected county first via the Upload tab

### "External Analysis Error: Ensure Colab/Gemini backend is active"
**Solution**: 
1. Check that the backend server is running (`python main.py`)
2. Verify `GOOGLE_API_KEY` is set in `.env.local`
3. Ensure you have internet connectivity for Gemini API

### Comparison takes too long
**Note**: Processing large PDFs can take 30-60 seconds. This is normal as Gemini analyzes both documents thoroughly.

## Technical Details

### What Happens Behind the Scenes?
1. **Upload**: Both PDFs are uploaded to Gemini's file API
2. **Processing**: Gemini's AI reads both documents simultaneously
3. **Extraction**: AI locates county-specific sections (3.X.1 - 3.X.16 in CBIRR)
4. **Comparison**: Values are extracted and compared
5. **Scoring**: Integrity score is calculated based on discrepancies
6. **Reporting**: Results are formatted and displayed

### Data Sources
- **Official Data**: CBIRR 2024/25 Report, Controller of Budget
- **Pushed Data**: County-uploaded budget documents
- **Sections Referenced**: 
  - 3.X.2 (OSR), 3.X.5 (Revenue), 3.X.6 (Dev Exp)
  - 3.X.7 (Rec Exp), 3.X.8 (Wage Bill), 3.X.14 (Pending Bills)

## Best Practices

1. **Always upload the official CBIRR first** before running comparisons
2. **Start with one merit** to understand the feature before running full audits
3. **Review source citations** to verify where data was extracted from
4. **Check data quality notes** for context on data completeness
5. **Use multiple merits** for comprehensive integrity assessment

## Next Steps

After running a comparison:
1. **Export Results**: (Coming soon) Download PDF/Excel reports
2. **Track Trends**: (Coming soon) Compare scores over time
3. **Share Findings**: Use the integrity scorecard for advocacy or reporting
4. **Deep Dive**: Review specific sections in the PDFs based on alerts

---

**Need Help?** Check the full implementation documentation in `PDF_PUSH_COMPARE_IMPLEMENTATION.md`
