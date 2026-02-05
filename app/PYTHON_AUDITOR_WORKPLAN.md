# Auditor Workplan

- [x] **Phase 1: Deep Extraction Enhancement**
  - Ensure `SmartPageLocator` grabs the full county section (approx 12-15 pages to cover sections 3.X.1 to 3.X.16).
  - Verify `ContextAwareSlicer` handles the full range of headers.
- [x] **Phase 2: Senior Auditor Logic (Groq Stage)**
  - Update prompt to synthesized Pillars: Revenue, Expenditure, Liability.
  - Implement the "Fiscal Health Verdict" logic.
  - Add National Context (Peer comparisons).
- [x] **Phase 3: Pipeline Restoration**
  - Remove debug "Early Exit" from `hybrid_processor.py`.
  - Connect refined extraction results to the new Auditor prompt.
- [ ] **Phase 4: Frontend Validation**
  - Verify the report displays correctly with synthesis. (UI Updated, Pending Test)
