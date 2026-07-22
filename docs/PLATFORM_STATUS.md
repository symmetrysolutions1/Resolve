# Resolve platform status

This file tracks the ticket, bounty, freelance, and hackathon platforms reviewed
for Resolve. It is an operating checklist, not a marketing list: a platform is
only "active" when the account/session was confirmed and we can realistically
use it for work discovery or applications.

Last verification: July 2026, from the Symmetry Chrome session and public
GitHub/Devpost checks.

## Active now

| Platform | Use | Account/profile status | Operational status | Notes |
|---|---|---|---|---|
| Upwork | Freelance jobs, invites, paid contracts | Logged in as Alejandro Realpe Rivera, freelancer profile available | Active with limits | Can browse jobs and respond to invites. Normal proposals require Connects. Working style assessment remains a profile improvement item. |
| Algora | Open-source bounties and dev opportunities | Logged in as `symmetrysolutions1` / SymmetryEnterprise | Active | Profile exists. Can browse bounty/job opportunities. Resume/preferences and payout details should be completed before serious payouts. |
| Opire | Open-source bounties | Logged in as `symmetrysolutions1` | Active | Dashboard and bounty list visible. Good source for unclaimed and priced issues; still requires per-ticket preflight before working. |
| Superteam Earn | Crypto/web3 bounties, grants, jobs | Logged in as Alejandro | Active | Homepage shows "Welcome back, Alejandro" and current bounties/projects/grants. Strong source for crypto opportunities, but many listings are contests, grants, region-restricted, or require capital. |
| GitHub | Source, issue validation, portfolio, public repos | `symmetrysolutions1/Resolve` public; `testigosdigitalesCOL/presidencia2026-2` public | Active | Resolve is the operating repo. E14 is visible for hackathon review. |
| Devpost | Hackathons and project submissions | OpenAI Build Week submissions visible as submitted | Active for hackathons | Not a normal ticket marketplace, but useful for prize opportunities and portfolio signals. |

## Pending confirmation / setup

| Platform | Intended use | Current observed state | Next action |
|---|---|---|---|
| Contra | Freelance services / portfolio | Not logged in; public homepage shows Sign up / Log in | Log in or create account, then publish services and payout setup. |
| Fiverr | Freelance gigs | Dashboard URL partially loaded but automation could not verify; previously showed human/bot verification | Complete human verification manually, then confirm seller profile/gigs. |
| Freelancer | Freelance jobs | Redirected to login | Create/login account, complete profile, verify payment method before applying. |
| PeoplePerHour | Freelance jobs | Public login/home pages visible; no active session confirmed | Create/login account, complete freelancer profile, verify payout path. |
| IssueHunt | Open-source bounties | Public funded-issues list visible without login; GitHub sign-in still pending | Low priority. Public list has mostly small rewards and many PRs; sign in only if we find a worthwhile issue. |

## Not active / deprioritized

| Platform | Reason | Decision |
|---|---|---|
| OnlyDust | The site reports that OnlyDust has closed/discontinued service | Remove from active ticket pipeline unless the service relaunches. |
| TaskBounty | Current site focuses on app-security scanning/autopilot services, not the original bounty marketplace flow we expected | Deprioritize as a bounty source; revisit only if we want security-service lead generation. |

## Specialized security and audit platforms for later

These are not first-wave Resolve channels. They can pay well but require a
stronger security track record and stricter scope control.

| Platform | Use | Status |
|---|---|---|
| Immunefi | Web3 security bounties | Later |
| Code4rena | Competitive audits | Later |
| Sherlock | Competitive audits | Later |
| Cantina | Competitive audits | Later |

## Daily operating order

1. Check Upwork invites first because invites do not cost Connects.
2. Check Opire for priced issues with zero solvers.
3. Check Algora for fresh, unclaimed bounties and validate GitHub issue state.
4. Check Superteam for crypto opportunities, but reject contests/grants unless the payout path and odds are clear.
5. Use IssueHunt only as a low-priority public scan source.
6. Use Contra/Fiverr/Freelancer/PeoplePerHour only after profiles are complete.
7. Keep Devpost and similar hackathons as prize/portfolio opportunities, not the daily ticket pipeline.

## Preflight before working any ticket

Before starting work, Resolve must confirm:

- payout amount and payment channel;
- issue/ticket still open;
- repository exists and is safe to inspect;
- no active competing PR or assigned solver;
- no region restriction blocking Colombia;
- no upfront capital required unless explicitly approved;
- expected hourly value meets the current floor;
- scope is clear enough to deliver without unpaid discovery.
