import React, { useEffect, useMemo, useRef, useState } from "react";
import briefMock from "./mocks/brief_example.json";
import sourcesMock from "./mocks/sources_example.json";
import JSZip from "jszip";
import { saveAs } from "file-saver";

// tokens
const PILL_FOCUS = "focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#2D7FF9]";
const CARD = "rounded-2xl bg-[#141414] border border-white/10 shadow-sm";
const TAB = `px-4 py-3 rounded-lg ${PILL_FOCUS}`;
const MUTED = "text-white/70";
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

function Pill({ label }) { return <span className="px-2 py-1 bg-white/10 rounded-lg text-xs">{label}</span>; }
function Button({ label, onClick }) { return <button onClick={onClick} className={`px-3 py-2 bg-white/10 hover:bg-white/15 rounded-lg text-sm ${PILL_FOCUS}`}>{label}</button>; }
function Tab({ label, active, onClick }) {
  return <button className={`${TAB} ${active ? "bg-white/10" : "bg-transparent hover:bg-white/5"}`} onClick={onClick}>{label}</button>;
}

export default function Panel1() {
  const [q, setQ] = useState("");
  const [k, setK] = useState(5);
  const [activeTab, setActiveTab] = useState("DOSSIER"); // DOSSIER|SOURCES|INSPECTOR
  const [brief, setBrief] = useState(null);
  const [sources, setSources] = useState([]);
  const [telemetry, setTelemetry] = useState([]);
  const [p95, setP95] = useState(3.4);
  const [cacheHit, setCacheHit] = useState(0);
  const [sourcesOpen, setSourcesOpen] = useState(false); // collapsed by default
  const [showReceipts, setShowReceipts] = useState(false);
  const [loading, setLoading] = useState(false);
  const askInputRef = useRef(null);

  // shortcuts: '/', 'r', 'e'
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "/") { e.preventDefault(); askInputRef.current?.focus(); }
      if (e.key.toLowerCase() === "r") redo();
      if (e.key.toLowerCase() === "e") exportAuditZip();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [brief, sources, telemetry]);

  // first load → mocks
  useEffect(() => {
    setBrief(briefMock);
    setSources(sourcesMock);
    setSourcesOpen(true); // auto-open on first result
    fetch("/src/apps/augury-panel/mocks/telemetry.jsonl")
      .then(r => r.text())
      .then(t => setTelemetry((t || "").trim().split("\n").slice(-10)))
      .catch(() => setTelemetry([]));
  }, []);

  const sourceIndex = useMemo(() => new Map(sources.map((s, i) => [s.chunk_id, i])), [sources]);
  const top3 = sources.slice(0, 3);
  const moreCount = Math.max(0, sources.length - top3.length);

  async function runAsk() {
    setLoading(true);
    try {
      // LIVE (later):
      // const t0 = performance.now();
      // const res = await fetch(`${API_BASE}/ask?q=${encodeURIComponent(q)}&k=${k}`);
      // const json = await res.json();
      // map → setSources(...); setP95(Math.round(performance.now()-t0)); setCacheHit(1);

      // MOCK:
      const filtered = q ? sourcesMock.filter(s => s.snippet.toLowerCase().includes(q.toLowerCase())) : sourcesMock;
      setSources(filtered);
      setCacheHit(1);
      setSourcesOpen(true);
    } finally { setLoading(false); }
  }

  async function runBrief() {
    setLoading(true);
    try {
      // LIVE (later):
      // const res = await fetch(`${API_BASE}/brief?q=${encodeURIComponent(q)}&k=${k}`);
      // const data = await res.json();
      // setBrief(data);
      setBrief(briefMock);
      setActiveTab("DOSSIER");
    } finally { setLoading(false); }
  }

  function redo() { if (q || sources.length) runAsk(); }

  async function exportAuditZip() {
    if (!brief) return;
    const zip = new JSZip();
    zip.file("dossier.json", JSON.stringify(brief, null, 2));
    zip.file("receipts.jsonl", telemetry.join("\n") || '{"note":"telemetry sample"}');
    const blob = await zip.generateAsync({ type: "blob" });
    saveAs(blob, "augury_audit_bundle.zip");
  }

  return (
    <div className="min-h-screen bg-[#0E0E0E] text-white">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-white/10 bg-[#0E0E0E]/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div className="font-semibold">Augury</div>
          <div className="hidden lg:flex items-center gap-3 text-sm">
            <Pill label={`p95 ${p95} ms`} />
            <Pill label={`corpus 9,472`} />
            <Pill label={`backend numpy`} />
            <button className={`text-xs ${PILL_FOCUS}`} onClick={()=>setShowReceipts(true)}>Receipts ✓</button>
            <div className="ml-3 flex gap-2">
              <Button onClick={redo} label="Redo" />
              <Button onClick={runBrief} label="Refine" />
              <Button onClick={exportAuditZip} label="Export" />
              <Button onClick={()=>navigator.clipboard.writeText(JSON.stringify(brief ?? {}, null, 2))} label="Copy" />
            </div>
          </div>
        </div>
      </header>

      {/* Ask bar */}
      <section className="mx-auto max-w-3xl px-4 pt-8">
        <div className={`${CARD} p-4`}>
          <div className="flex items-center gap-3">
            <input
              ref={askInputRef}
              value={q}
              onChange={(e)=>setQ(e.target.value)}
              onKeyDown={(e)=>{ if (e.key === "Enter") runAsk(); }}
              placeholder="What do you want to verify?"
              className={`flex-1 bg-transparent outline-none placeholder-white/40 text-lg ${PILL_FOCUS}`}
            />
            <label className={`${MUTED} text-sm`}>k</label>
            <input
              type="number" min={1} max={20} value={k}
              onChange={(e)=>setK(Math.max(1, Math.min(20, Number(e.target.value))))}
              className={`w-16 bg-[#0B0B0B] border border-white/10 rounded-lg px-2 py-1 text-right ${PILL_FOCUS}`}
            />
            <Button onClick={runAsk} label={loading ? "Running…" : "Run"} />
          </div>
          <div className="mt-2 text-xs">
            {cacheHit ? <span className="text-green-400">Cached</span> : "Warm-up suggested"} · Press <kbd className="px-1 border rounded">/</kbd> to focus
          </div>
        </div>
      </section>

      {/* Main */}
      <main className="mx-auto max-w-6xl px-4 py-6 grid grid-cols-12 gap-6">
        {/* Left */}
        <div className="col-span-12 lg:col-span-8">
          <div className="flex items-center gap-2 mb-3">
            <Tab label="Dossier" active={activeTab==="DOSSIER"} onClick={()=>setActiveTab("DOSSIER")} />
            <Tab label="Sources" active={activeTab==="SOURCES"} onClick={()=>setActiveTab("SOURCES")} />
            <Tab label="Inspector" active={activeTab==="INSPECTOR"} onClick={()=>setActiveTab("INSPECTOR")} />
          </div>

          {activeTab==="DOSSIER" && (
            <DossierView
              brief={brief}
              sourceIndex={useMemo(()=>new Map(sources.map((s,i)=>[s.chunk_id,i])),[sources])}
              onClickCitation={(chunkId)=>{
                setActiveTab("SOURCES"); setSourcesOpen(true);
                const el = document.getElementById(`src-${chunkId}`);
                if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
              }}
            />
          )}

          {activeTab==="SOURCES" && <SourcesDock sources={sources} open={sourcesOpen} setOpen={setSourcesOpen} />}

          {activeTab==="INSPECTOR" && (
            <div className={`${CARD} p-4`}>
              <div className="text-sm font-medium mb-2">Telemetry (last 10)</div>
              <pre className="text-xs whitespace-pre-wrap leading-5">{telemetry.join("\n") || "Run an action to view telemetry."}</pre>
            </div>
          )}
        </div>

        {/* Right preview dock (top-3) */}
        <aside className="hidden lg:block col-span-4">
          <div className={`${CARD} p-4`}>
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium">Sources</div>
              <button className={`text-xs ${PILL_FOCUS}`} onClick={()=>setSourcesOpen(!sourcesOpen)}>
                {sourcesOpen ? "Collapse" : "Expand"}
              </button>
            </div>
            {!sources.length && <div className={`${MUTED} text-sm mt-3`}>Ask to load evidence. No raw PII.</div>}
            {!!sources.length && (
              <div className="mt-3 space-y-3">
                {top3.map((s)=>(
                  <div id={`src-${s.chunk_id}`} key={s.chunk_id} className="border border-white/10 rounded-xl p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono">{s.chunk_id}</span>
                      <span className="text-xs">{(s.score*100).toFixed(0)}%</span>
                    </div>
                    <p className="text-sm mt-2">{s.snippet}</p>
                  </div>
                ))}
                {moreCount>0 && <div className={`${MUTED} text-xs`}>+{moreCount} more (open full Sources tab)</div>}
              </div>
            )}
          </div>
        </aside>
      </main>

      {/* Receipts modal */}
      {showReceipts && (
        <div role="dialog" aria-modal="true" className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center">
          <div className={`${CARD} p-5 w-full max-w-lg`}>
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium">Receipts</div>
              <button className={`text-xs ${PILL_FOCUS}`} onClick={()=>setShowReceipts(false)}>Close</button>
            </div>
            <pre className="text-xs whitespace-pre-wrap leading-5">
{JSON.stringify(brief?.receipts ?? {}, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

function DossierView({ brief, sourceIndex, onClickCitation }) {
  if (!brief) return <div className={`${CARD} p-6 ${MUTED}`}>Run a brief to generate a decision.</div>;
  return (
    <article className={`${CARD} p-6 space-y-5`}>
      <h2 className="text-2xl font-semibold">Dossier</h2>
      <p className="text-lg">{brief.executive_summary}</p>
      {brief.synthesized_response?.map((pt, i)=>(
        <section key={i} className="mt-3">
          <div className="flex items-start gap-2">
            <span className="text-white/60">{i+1}.</span>
            <div>
              <p className="text-base leading-7">
                {pt.point}{" "}
                {pt.supporting_evidence?.map((ev, j) => {
                  const n = sourceIndex.has(ev.chunk_id) ? (sourceIndex.get(ev.chunk_id) + 1) : j+1;
                  return (
                    <button
                      key={ev.chunk_id+"-"+j}
                      onClick={()=>onClickCitation(ev.chunk_id)}
                      className={`align-super text-xs text-[#7FB3FF] underline-offset-2 hover:underline ${PILL_FOCUS}`}
                      aria-label={`View source ${n}`}
                    >[{n}]</button>
                  );
                })}
              </p>
              {typeof pt.confidence === "number" && <div className="text-xs text-white/60 mt-1">confidence {(pt.confidence*100).toFixed(0)}%</div>}
            </div>
          </div>
        </section>
      ))}
    </article>
  );
}

function SourcesDock({ sources, open, setOpen }) {
  return (
    <div className={`${CARD} p-4`}>
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium">Sources</div>
        <button className={`text-xs ${PILL_FOCUS}`} onClick={()=>setOpen(!open)}>{open ? "Collapse" : "Expand"}</button>
      </div>
      {!sources.length && <div className={`${MUTED} text-sm mt-3`}>Ask to load evidence. No raw PII.</div>}
      {open && !!sources.length && (
        <div className="mt-3 space-y-3">
          {sources.map((s)=>(
            <div id={`src-${s.chunk_id}`} key={s.chunk_id} className="border border-white/10 rounded-xl p-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono">{s.chunk_id}</span>
                <span className="text-xs">{(s.score*100).toFixed(0)}%</span>
              </div>
              <p className="text-sm mt-2">{s.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
