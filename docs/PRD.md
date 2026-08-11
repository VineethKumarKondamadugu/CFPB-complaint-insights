# Product Requirements Document (PRD)

## Project Title
**CFPB Complaint Insights Platform (Internal Compliance Tool)**

## Version
v1.0

## Date
August 11, 2026

## Author
Product Management / AI Architecture

---

## 1. Executive Summary

The CFPB Complaint Insights Platform is an internal analytics and AI application designed for compliance teams to extract actionable insights from Consumer Financial Protection Bureau (CFPB) complaint data and internal customer feedback.

The platform will ingest a rolling six-month subset of CFPB complaint data on weekly and monthly cadences, analyze complaint narratives using AI/NLP, classify complaints using CFPB taxonomy, identify trend shifts, and generate explainable insights through an interactive dashboard. Users will also be able to upload internal feedback files (CSV/XLSX) to analyze them against the same taxonomy and compare internal trends against CFPB baselines.

This document defines the MVP scope, requirements, constraints, risks, and roadmap.

---

## 2. Problem Statement

Compliance teams need a faster and more structured way to identify emerging risks and recurring issues from large volumes of complaint data. Current approaches are often manual, reactive, and inconsistent across sources.

There is a need for an internal system that:
- Continuously analyzes CFPB complaints,
- Detects weekly/monthly movement in complaint categories and themes,
- Provides explainable AI outputs,
- Allows internal customer feedback uploads for side-by-side benchmarking,
- Generates compliance-ready downloadable reports on demand.

---

## 3. Objectives

### 3.1 Business Objectives
- Improve speed of compliance insight generation.
- Increase early detection of complaint-related risk trends.
- Standardize complaint analysis using CFPB-aligned taxonomy.
- Reduce manual effort in reporting and thematic analysis.

### 3.2 Product Objectives
- Deliver a dashboard with trend, category, sentiment, and topic insights.
- Enable ingestion and AI analysis of both CFPB and uploaded internal feedback.
- Provide clear explainability for AI classifications and trend outputs.
- Support on-demand report export for compliance review workflows.

---

## 4. Target Users

### Primary Persona
**Compliance Analysts and Compliance Managers (Internal Team)**

### Secondary Persona
**Compliance Leadership / Risk Review Stakeholders**

### User Needs
- Monitor high-level risk indicators quickly.
- Drill into category and theme drivers.
- Compare internal feedback with external CFPB complaint trends.
- Trust model outputs through transparent rationale.
- Export findings for governance and review meetings.

---

## 5. Scope

## 5.1 In Scope (MVP)
1. CFPB complaint ingestion (rolling last 6 months).
2. Scheduled refresh pipelines (weekly and monthly).
3. Upload ingestion for CSV/XLSX files.
4. AI categorization using CFPB taxonomy.
5. Keyword extraction and trend analysis (WoW and MoM).
6. Topic clustering.
7. Sentiment analysis (3-class: Positive, Neutral, Negative).
8. Explainability artifacts (confidence, evidence snippets, low-confidence warnings).
9. Interactive dashboard with filters and drilldowns.
10. On-demand downloadable reports (PDF and CSV).

## 5.2 Out of Scope (MVP)
- Real-time streaming ingestion.
- External customer-facing or multi-tenant SaaS capabilities.
- Forecasting and predictive risk scoring.
- Automated alert integrations (email/Slack/Teams).
- Advanced role-based access controls beyond basic internal access.
- Formal compliance certifications/workflows (e.g., SOC2 programmatic controls).
- Multilingual NLP.

---

## 6. Data Sources and Inputs

## 6.1 CFPB Data
- Source: CFPB complaint database.
- Data window: rolling **last 6 months**.
- Refresh cadence:
  - Weekly refresh
  - Monthly refresh

## 6.2 User Uploads
- Supported file types: **CSV, XLSX**
- Expected schema: CFPB-compatible columns.
- Upload policy: ingest all provided CFPB-aligned columns.

## 6.3 Required Columns for AI Processing
Even if full schema is accepted, the following are mandatory for full NLP analysis:
- Complaint narrative text field (CFPB-equivalent)
- Complaint date field (CFPB-equivalent)

## 6.4 Optional Columns
Any other CFPB-style fields (e.g., product, issue, company, state, channel, tags) are optional but should be ingested when present.

---

## 7. Core Use Cases

1. **Weekly risk review**  
   Compliance analyst reviews weekly category and keyword shifts.

2. **Monthly trend review**  
   Compliance manager reviews monthly trend and sentiment movement by category.

3. **Internal feedback benchmarking**  
   Analyst uploads internal feedback and compares internal themes against CFPB data.

4. **Explainable AI review**  
   User inspects low-confidence classifications and associated evidence terms/snippets.

5. **Report generation**  
   User exports an on-demand PDF summary and CSV data slice for stakeholder review.

---

## 8. Functional Requirements

### FR-1: CFPB Ingestion Pipeline
- System shall ingest CFPB complaint records for a rolling 6-month window.
- System shall support separate weekly and monthly refresh jobs.
- System shall maintain ingestion run history and data freshness metadata.

### FR-2: Upload Ingestion and Validation
- System shall allow CSV and XLSX uploads.
- System shall validate schema compatibility and required fields.
- System shall provide row-level validation feedback with failure reasons.

### FR-3: Data Storage and Normalization
- System shall normalize and store CFPB and uploaded data in a unified analytical model.
- System shall preserve source identifiers (CFPB vs uploaded).

### FR-4: Taxonomy Classification
- System shall classify complaint records into CFPB taxonomy categories.
- System shall return confidence scores for each classification.
- System shall flag low-confidence predictions with a warning state.

### FR-5: Keyword Extraction
- System shall extract relevant keywords from complaint narratives.
- System shall rank keywords by frequency and trend movement.

### FR-6: Topic Clustering
- System shall generate topic clusters from complaint text.
- System shall present clusters at overall and category-level views.

### FR-7: Sentiment Analysis
- System shall classify sentiment into three classes: Positive, Neutral, Negative.
- System shall provide sentiment distributions and trend movement over time.

### FR-8: Trend Analytics
- System shall compute week-over-week and month-over-month deltas for:
  - complaint volumes,
  - category counts,
  - keyword usage,
  - topic prevalence,
  - sentiment mix.

### FR-9: Explainability
- System shall expose rationale for AI outputs through:
  - confidence scores,
  - evidence terms/snippets,
  - trend deltas with supporting contributors.

### FR-10: Dashboard
- System shall provide visualizations for:
  - complaint volume trend,
  - category distribution,
  - rising/falling keywords,
  - topic clusters,
  - sentiment by category/time,
  - low-confidence prediction queue.
- System shall support filtering (time range, category, product, source, etc.).

### FR-11: Reporting and Export
- System shall generate on-demand **PDF** reports from current dashboard filters.
- System shall export filtered data as **CSV**.

---

## 9. Non-Functional Requirements

### NFR-1: Accuracy
- Classification precision target: **>= 80%** on agreed validation dataset.

### NFR-2: Performance
- Dashboard interactions and common filtered queries should return within acceptable internal SLA (to be finalized during design).

### NFR-3: Reliability
- Scheduled data jobs must include retry logic and status monitoring.

### NFR-4: Security
- Internal authenticated access only.
- Encryption in transit and at rest.

### NFR-5: Explainability & Trust
- AI outputs must include confidence and rationale artifacts visible in UI.

### NFR-6: Auditability
- System should log model/prompt/version metadata and processing timestamps for reproducibility.

---

## 10. Assumptions

1. CFPB data structure remains sufficiently stable for ongoing ingestion.
2. Complaint narrative coverage is adequate for NLP insight generation.
3. Internal users accept decision-support AI with explainability rather than deterministic categorization.
4. Basic internal security controls are sufficient for MVP.
5. Weekly trend analysis will require noise controls for low sample buckets.

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Inconsistent/short narrative text | Reduced AI quality | Data quality thresholds, fallback handling |
| Weekly sample volatility | False trend spikes | Minimum volume thresholds, smoothing, confidence bands |
| Upload schema variability | Processing failures | CFPB-compatible template, header mapping, row-level errors |
| Low trust in model outputs | Reduced adoption | Confidence + evidence snippets + low-confidence warning panel |
| Category ambiguity | Precision degradation | Confidence gating and "needs review" handling |

---

## 12. Success Metrics (First 60 Days)

1. **Adoption:** >= 70% of compliance users perform weekly dashboard reviews.
2. **Upload engagement:** >= 50% of users upload at least one CSV/XLSX file.
3. **Reporting utilization:** >= 60% of active users generate PDF and/or CSV exports.
4. **Model trust score:** average explainability usefulness >= 4/5 (internal survey).
5. **Model quality:** taxonomy classification precision maintained at or above 80%.

---

## 13. MVP Release Criteria

The MVP is considered release-ready when all conditions below are met:

1. CFPB weekly/monthly pipelines are operational for rolling 6-month data.
2. CSV/XLSX upload pipeline validates and processes CFPB-compatible files.
3. AI modules deliver taxonomy classification, keyword trends, topic clustering, and 3-class sentiment.
4. Low-confidence outputs are explicitly flagged in the UI.
5. Dashboard supports required visualizations and filtering.
6. On-demand PDF and CSV exports are functional.
7. Measured classification precision meets >= 80% on validation benchmark.

---

## 14. Roadmap Beyond MVP

### Phase 2 (V1.1)
- Scheduled report automation.
- User correction loop for misclassification feedback.
- Basic anomaly detection.

### Phase 3 (V2)
- Alerting integrations (email/Slack/Teams).
- Forecasting and risk projection.
- Conversational insights assistant.
- Extended benchmarking dimensions (peer/product/state-level).

---

## 15. Open Decisions for Engineering Design (Post-PRD)

1. Final internal SLA targets for dashboard and export performance.
2. Confidence threshold values for low-confidence warning states.
3. Topic clustering strategy and explainability format details.
4. Data retention period and archival policy for uploads.
5. Monitoring and observability stack for ingestion/model pipelines.

---

## 16. Summary

This MVP delivers a practical and explainable internal compliance intelligence platform that combines CFPB trend monitoring with AI-assisted analysis of internal feedback. The scope is intentionally focused on high-value compliance workflows: trend detection, taxonomy alignment, explainability, and on-demand reporting. The design supports near-term operational utility while laying the foundation for alerts, forecasting, and deeper intelligence in future releases.
