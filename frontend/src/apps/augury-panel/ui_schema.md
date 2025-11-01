# UI ↔ API Map — Panel-1 (Perplexity-style)

AskBar → GET /ask?q&k
  → SourcesDock.items[] = {chunk_id, score, snippet}  (from /ask or _debug_evidence)

Brief  GET /brief?q&k[&debug=1]
   DossierView:
      executive_summary  brief.executive_summary
      claims (inline [n])  brief.synthesized_response[{point, supporting_evidence[]}]
       - [n] maps to supporting_evidence[].chunk_id
     • contradictions ← brief.contradictions_identified[]
     • next_questions ← brief.next_questions_uncovered[]
  → ReceiptsPill:
     • {config_hash, dataset_hash, timestamp} ← brief.receipts

InspectorDrawer  last 10 telemetry lines (env-gated stdout)

Export (Audit Zip)  bundle:
   dossier.json (entire /brief)
   receipts.jsonl (telemetry slice)
