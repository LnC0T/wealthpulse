# Pricing + Stripe Setup Guide (Draft)

## Suggested Pricing Tiers
You can adjust, but this fits the market and the unique value of WealthPulse.

1. **Starter**
   - Target: basic users
   - Price: $5-8/mo or $51-77/yr
   - Features: core tracking, local storage, basic reports

2. **Pro**
   - Target: business owners and serious planners
   - Price: $10-17/mo or $102-170/yr
   - Features: entities, trust tools, premium analytics, exports

3. **Elite**
   - Target: advanced users + community tools
   - Price: $21-34/mo or $204-340/yr
   - Features: marketplace, advanced alerts, premium data, advisor pack

4. **Founder**
   - Target: early supporters + power users
   - Price: one-time or lifetime option (founding member)
   - Features: all Elite features, founder badge, early access releases

## Stripe Setup (Simple Launch)
1. Create a Stripe account and verify business details
2. Add products in Stripe:
   - WealthPulse Starter (monthly + annual)
   - WealthPulse Pro (monthly + annual)
   - WealthPulse Elite (monthly + annual)
3. Set payment links or build a checkout page
4. Add webhook for subscription status updates
5. Store Stripe API keys securely (never hardcode)

## Minimal Implementation Path
- Use Stripe Payment Links for quick launch
- On payment success, issue a license key or account unlock
- Maintain a "license status" table in Supabase (optional)

## What You Need on the App Side
- A "Subscription" panel in Settings
- Display plan name + renewal date
- Lock premium features if plan inactive

---

Note: This is guidance only. Review billing and tax requirements for your region.
