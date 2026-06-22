# User Stories

## Registered Customer

**US-01** — Pre-Allocation Visibility  
As a registered customer, I want to know which unit has been pre-allocated to me before Allocation Day, so that I can prepare and log in on time.

**US-02** — Competitive Booking  
As a registered customer, I want to see my pre-allocated unit on Allocation Day and pay first to secure it, so that I get my preferred unit.

**US-03** — Auto Drop to Next Unit (Case 1 — Outcompeted)  
As a registered customer, if someone else pays for my pre-allocated unit before me, I want the system to automatically move me to the next available unit in the same category, so that I don't have to restart my search manually.

**US-04** — Hold on Next Unit (Case 2 — Late Login)  
As a registered customer, if I log in late, I want the system to hold the next available unit for me for up to 30 minutes, so that I have a fair chance to pay for it.

**US-05** — Tower Change on Full Drop (Case 3 — All Bands Exhausted)  
As a registered customer, if all bands in my current tower are exhausted, I want the system to move me to the next tower in sequence (starting from the top band), so that I'm never left without an option.

**US-06** — Cancellation Request  
As a registered customer, I want to cancel my booking by clicking a cancel button and confirming twice, so that I can initiate a refund if I change my mind.

**US-07** — Refund Status Visibility  
As a registered customer, I want to see the current status of my cancellation/refund request on the portal, so that I know where it stands in the approval process.

---

## Admin / Strategy Team

**US-08** — Inventory Gate Control  
As an admin, I want to enable 2nd and 3rd preference towers on allocation day based on demand, so that we don't open non-RERA inventory unnecessarily.

**US-09** — Manual Unit Assignment  
As an admin, I want to manually assign a GHNG number to a specific unit, so that I can accommodate special cases or corrections before allocation day.

**US-10** — Allocation Dashboard  
As an admin, I want a dashboard showing allocated and waitlisted customers per unit and per tower in real time, so that I can monitor the event and intervene when needed.

---

## M&SS Team

**US-11** — Cancellation Approval  
As an M&SS officer, I want to review cancellation requests with full customer details and Easebuzz transaction ID, and approve or reject them with a reason, so that only valid cancellations proceed to Finance.

**US-12** — Refund Pipeline Dashboard  
As an M&SS officer, I want a linear dashboard view of all cancellation cases with stage status (green check / red cross), so that I can track every case end-to-end.

---

## Finance Team

**US-13** — Finance-Level Refund Approval  
As a Finance officer, I want to review M&SS-approved cancellations, see full customer details and Easebuzz transaction ID, and approve or reject with a reason, so that refunds are financially validated before going to Pre-Audit.

---

## Pre-Audit Team

**US-14** — Pre-Audit Approval  
As a Pre-Audit officer, I want to review Finance-approved cancellations and approve or reject with a reason, so that refunds are audited before Banking processes them.

---

## Banking Team

**US-15** — Refund Execution  
As a Banking officer, I want to view Pre-Audit-approved cases and enter a refund reference ID upon execution, so that all departments can see the refund has been processed.
