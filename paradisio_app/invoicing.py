"""
Paradisio Invoicing — SINPE Móvil payment tracking, invoice generation, revenue reports.

Usage:
  python invoicing.py create "Business Name" featured|pro    Create invoice
  python invoicing.py list                                    List all invoices
  python invoicing.py pay INV-2026-0001 --ref "SINPE1234"    Mark paid
  python invoicing.py cancel INV-2026-0001                   Cancel invoice
  python invoicing.py report                                  Revenue summary
  python invoicing.py build                                   Generate invoice HTML pages
"""
import json
import sys
from datetime import datetime, date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
INVOICES_PATH = BASE / "docs" / "paradisio_app" / "data" / "invoices.json"
OUTPUT_DIR = BASE / "docs" / "paradisio_app" / "invoices"

TIERS = {
    "featured": {"usd": 100, "crc": 52500, "label": "Featured Listing"},
    "pro": {"usd": 200, "crc": 105000, "label": "Pro Listing"},
}

CRC_PER_USD = 525


def load():
    if INVOICES_PATH.exists():
        return json.loads(INVOICES_PATH.read_text(encoding="utf-8"))
    return []


def save(invoices):
    INVOICES_PATH.parent.mkdir(parents=True, exist_ok=True)
    INVOICES_PATH.write_text(json.dumps(invoices, indent=2, ensure_ascii=False), encoding="utf-8")


def next_id(invoices):
    existing = [i["invoice_id"] for i in invoices]
    n = 1
    while f"INV-2026-{n:04d}" in existing:
        n += 1
    return f"INV-2026-{n:04d}"


def cmd_create(args):
    name = " ".join(args.name)
    tier = args.tier.lower()
    if tier not in TIERS:
        print(f"Invalid tier: {tier}. Choose: featured, pro")
        return
    invoices = load()
    inv = {
        "invoice_id": next_id(invoices),
        "business_name": name,
        "tier": tier,
        "amount_usd": TIERS[tier]["usd"],
        "amount_crc": TIERS[tier]["crc"],
        "issued_date": date.today().isoformat(),
        "status": "pending",
        "paid_date": None,
        "sinpe_reference": None,
        "valid_until": None,
        "notes": "",
    }
    invoices.append(inv)
    save(invoices)
    print(f"Created {inv['invoice_id']} — {name} ({TIERS[tier]['label']})")
    print(f"  Amount: ${inv['amount_usd']} USD / ₡{inv['amount_crc']:,} CRC")
    print(f"  Status: {inv['status']}")
    print(f"  Invoice page: invoices/{inv['invoice_id']}.html")


def cmd_list(args):
    invoices = load()
    if not invoices:
        print("No invoices found.")
        return
    print(f"{'ID':20s} {'Business':35s} {'Tier':12s} {'Amount':10s} {'Status':10s} {'Paid':12s}")
    print("-" * 100)
    for i in invoices:
        paid = i.get("paid_date", "") or ""
        amt = f"${i['amount_usd']}"
        print(f"{i['invoice_id']:20s} {i['business_name'][:35]:35s} {i['tier']:12s} {amt:10s} {i['status']:10s} {paid:12s}")


def cmd_pay(args):
    invoices = load()
    for i in invoices:
        if i["invoice_id"] == args.invoice_id:
            i["status"] = "paid"
            i["paid_date"] = date.today().isoformat()
            if args.ref:
                i["sinpe_reference"] = args.ref
            # Valid for 1 year from issue
            issued = datetime.strptime(i["issued_date"], "%Y-%m-%d").date()
            i["valid_until"] = date(issued.year + 1, issued.month, issued.day).isoformat()
            save(invoices)
            print(f"Marked {args.invoice_id} as PAID")
            print(f"  Valid until: {i['valid_until']}")
            return
    print(f"Invoice {args.invoice_id} not found")


def cmd_cancel(args):
    invoices = load()
    for i in invoices:
        if i["invoice_id"] == args.invoice_id:
            i["status"] = "cancelled"
            save(invoices)
            print(f"Cancelled {args.invoice_id}")
            return
    print(f"Invoice {args.invoice_id} not found")


def cmd_report(args):
    invoices = load()
    total_pending = sum(i["amount_usd"] for i in invoices if i["status"] == "pending")
    total_paid = sum(i["amount_usd"] for i in invoices if i["status"] == "paid")
    total_cancelled = sum(i["amount_usd"] for i in invoices if i["status"] == "cancelled")
    paid_count = sum(1 for i in invoices if i["status"] == "paid")
    pending_count = sum(1 for i in invoices if i["status"] == "pending")

    print(f"\n{'='*50}")
    print(f"  PARADISIO — REVENUE REPORT")
    print(f"{'='*50}")
    print(f"  Date:     {date.today().isoformat()}")
    print(f"  Total invoices:  {len(invoices)}")
    print(f"  Paid:     {paid_count}  (${total_paid:,} USD / ₡{total_paid * CRC_PER_USD:,} CRC)")
    print(f"  Pending:  {pending_count}  (${total_pending:,} USD / ₡{total_pending * CRC_PER_USD:,} CRC)")
    print(f"  Cancelled:{sum(1 for i in invoices if i['status']=='cancelled')}  (${total_cancelled:,} USD)")
    print()

    if paid_count:
        print("  Paid invoices:")
        for i in invoices:
            if i["status"] == "paid":
                print(f"    {i['invoice_id']:20s} {i['business_name'][:35]:35s} ${i['amount_usd']:>4d}  {i.get('paid_date',''):12s} ref={i.get('sinpe_reference','') or '-'}")


def cmd_build(args):
    """Generate invoice HTML pages."""
    invoices = load()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = 0

    for inv in invoices:
        tier = TIERS[inv["tier"]]
        status_class = inv["status"]
        status_label = inv["status"].title()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Invoice {inv['invoice_id']} — Paradisio</title>
<link rel="stylesheet" href="../static/tokens.css">
<link rel="stylesheet" href="../static/styles.css">
<style>
  .invoice-page {{ max-width: 700px; margin: 2em auto; padding: 2em; background: var(--surface-raised); border-radius: 8px; }}
  .inv-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 2em; }}
  .inv-status {{ padding: 4px 12px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }}
  .inv-status.pending {{ background: #fff3cd; color: #856404; }}
  .inv-status.paid {{ background: #d4edda; color: #155724; }}
  .inv-status.cancelled {{ background: #f8d7da; color: #721c24; }}
  .inv-details {{ margin: 1.5em 0; }}
  .inv-details td {{ padding: 8px 12px; border-bottom: 1px solid var(--sand-50); }}
  .inv-details td:first-child {{ font-weight: 600; color: var(--muted); width: 160px; }}
  .inv-total {{ font-size: 1.3em; font-weight: 700; margin-top: 1em; }}
  .sinpe-section {{ margin-top: 2em; padding: 1.5em; background: var(--sand-50); border-radius: 8px; }}
  @media print {{ .no-print {{ display: none; }} }}
</style>
</head>
<body>
<div class="container invoice-page">
  <div class="inv-header">
    <div>
      <h1 style="margin:0">Paradisio</h1>
      <p style="margin:0;color:var(--muted);font-size:0.85em">Puerto Viejo Business Board</p>
    </div>
    <div style="text-align:right">
      <div class="inv-status {status_class}">{status_label}</div>
      <p style="margin:0.5em 0 0 0;font-size:0.85em;color:var(--muted)">{inv['invoice_id']}</p>
    </div>
  </div>

  <table class="inv-details">
    <tr><td>Business</td><td>{inv['business_name']}</td></tr>
    <tr><td>Plan</td><td>{tier['label']}</td></tr>
    <tr><td>Amount</td><td>${inv['amount_usd']} USD (₡{inv['amount_crc']:,} CRC)</td></tr>
    <tr><td>Issued</td><td>{inv['issued_date']}</td></tr>
    {f"<tr><td>Paid</td><td>{inv.get('paid_date','')}</td></tr>" if inv.get('paid_date') else ""}
    {f"<tr><td>Valid until</td><td>{inv.get('valid_until','')}</td></tr>" if inv.get('valid_until') else ""}
    {f"<tr><td>SINPE ref</td><td>{inv.get('sinpe_reference','')}</td></tr>" if inv.get('sinpe_reference') else ""}
  </table>

  <div class="sinpe-section">
    <p><strong>SINPE Móvil payment details:</strong></p>
    <p>Recipient: Oscar Aird / SkinnerBox Entertainment<br>
       SINPE: +506 8888 8888<br>
       Bank: BAC Credomatic</p>
    <p style="font-size:0.85em;color:var(--muted)">Reference: {inv['invoice_id']}</p>
  </div>

  <p class="no-print" style="margin-top:2em"><a href="../premium.html">&larr; Premium page</a></p>
</div>
</body>
</html>"""
        (OUTPUT_DIR / f"{inv['invoice_id']}.html").write_text(html, encoding="utf-8")
        generated += 1

    print(f"Generated {generated} invoice pages in {OUTPUT_DIR}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Paradisio Invoicing")
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Create invoice")
    p_create.add_argument("name", nargs="+")
    p_create.add_argument("tier", choices=["featured", "pro"])

    sub.add_parser("list", help="List invoices")

    p_pay = sub.add_parser("pay", help="Mark invoice paid")
    p_pay.add_argument("invoice_id")
    p_pay.add_argument("--ref", help="SINPE reference number")

    p_cancel = sub.add_parser("cancel", help="Cancel invoice")
    p_cancel.add_argument("invoice_id")

    sub.add_parser("report", help="Revenue summary")

    sub.add_parser("build", help="Generate invoice HTML pages")

    args = parser.parse_args()
    if args.command == "create":
        cmd_create(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "pay":
        cmd_pay(args)
    elif args.command == "cancel":
        cmd_cancel(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "build":
        cmd_build(args)
    else:
        parser.print_help()
