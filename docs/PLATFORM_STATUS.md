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
| PeoplePerHour | Freelance jobs | Logged in as Symmetry / `symmetry-enterprises-zxwnaqxq` | Partial active | Seller application exists and is open. Job title, bio, and GBP 12/h rate were drafted; profile still needs manual profile photo, skills, language, location confirmation, and application submission. |
| Fiverr | Freelance gigs | Logged in as `symmetryent` | Partial active | Buyer/client dashboard is accessible. Seller activation is blocked by human verification. |
| IssueHunt | Open-source bounties | Logged in as `symmetrysolutions1` | Active | Funded issues can be scanned and account settings were saved with JavaScript, TypeScript, Python, and Solidity skills. Many rewards are small, so prioritize micro-ticket economics. |
| GitHub | Source, issue validation, portfolio, public repos | `symmetrysolutions1/Resolve` public; `testigosdigitalesCOL/presidencia2026-2` public | Active | Resolve is the operating repo. E14 is visible for hackathon review. |
| Devpost | Hackathons and project submissions | OpenAI Build Week submissions visible as submitted | Active for hackathons | Not a normal ticket marketplace, but useful for prize opportunities and portfolio signals. |

## Pending confirmation / setup

| Platform | Intended use | Current observed state | Next action |
|---|---|---|---|
| Contra | Freelance services / portfolio | Signup verified for `symmetrysolutions1@gmail.com`; onboarding in progress | One-liner was drafted. Platform requires profile photo before account creation can finish. Then finish profile/services/payout. |
| Freelancer | Freelance jobs | Signup page shows Google option for `symmetrysolutions1@gmail.com`, but click did not advance in automation | Continue manually with Google or create account with Symmetry email, then complete profile/payment. |

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
5. Use IssueHunt for micro-tickets when reward/time math works and no PR competitor is active.
6. Use PeoplePerHour/Fiverr only after seller/applicant activation is complete.
7. Use Contra/Freelancer only after email/OAuth signup and profile setup are complete.
8. Keep Devpost and similar hackathons as prize/portfolio opportunities, not the daily ticket pipeline.

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

## Micro-ticket rule

Low rewards are not automatically rejected. A USD 1-40 reward can be useful when
the issue is real, open, payable, and simple enough for us to solve without
turning it into unpaid discovery.

Resolve should not reject micro-tickets only because the reward is small. The
decision is based on operational fit:

- issue/ticket is still open;
- payout path is visible;
- no active PR competitor or assigned solver;
- repo is safe to inspect;
- scope is clear enough to attempt;
- no upfront capital required;
- we can stop quickly if setup or scope becomes messy.

Small rewards are allowed as practice, portfolio, reputation, and cash-flow
opportunities.
