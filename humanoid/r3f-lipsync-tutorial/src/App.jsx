import { useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { Experience } from "./components/Experience";
import { API_BASE } from "./config";
import "./index.css";

export default function App() {
  const [mode, setMode] = useState("qa"); // "qa" | "lecture"

  // shared state to drive Avatar
  const [audioUrl, setAudioUrl] = useState(null);
  const [phonemes, setPhonemes] = useState(null);

  // ---- Q&A (upload) ----
  const [qaFile, setQaFile] = useState(null);
  async function sendQA() {
    if (!qaFile) return alert("Pick a WAV first.");
    const form = new FormData();
    form.append("file", qaFile);
    const r = await fetch(`${API_BASE}/ask`, { method: "POST", body: form });
    const data = await r.json();
    if (data.error) return alert(data.error);
    setAudioUrl(`${API_BASE}${data.audio_url}`);
    setPhonemes(data.phonemes);
  }

  // ---- Lectures ----
  const [lectures, setLectures] = useState([]);
  const [summary, setSummary] = useState("");
  const [lectureText, setLectureText] = useState("");
  const [selectedLectureId, setSelectedLectureId] = useState(null);

  async function loadLectures() {
    try{
      const r = await fetch(`${API_BASE}/lectures`);
      const data = await r.json();
      setLectures(Array.isArray(data) ? data : []);
    }catch(e){ console.error(e); }
  }
  useEffect(() => { loadLectures(); }, []);

  async function createLectureFromText() {
    if (!lectureText.trim()) return;
    const r = await fetch(`${API_BASE}/lectures`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "New Lecture", content: lectureText }),
    });
    const data = await r.json();
    setSummary(data.summary || "");
    await loadLectures();
  }

  async function openLecture(id) {
    setSelectedLectureId(id);
    const r = await fetch(`${API_BASE}/lectures/${id}`);
    const data = await r.json();
    setSummary(data.summary || "");
  }

  async function speakSummary() {
    if (!summary.trim()) return;
    const r = await fetch(`${API_BASE}/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: summary }),
    });
    const data = await r.json();
    if (data.error) return alert(data.error);
    setAudioUrl(`${API_BASE}${data.audio_url}`);
    setPhonemes(data.phonemes);
  }

  return (
    <div className="app">
      {/* ---- Sidebar ---- */}
      <aside className="sidebar">
        <h1 className="h1">Teaching Assistant <span className="badge">beta</span></h1>

        <div className="tabs">
          <button className={`tab ${mode === "qa" ? "active" : ""}`} onClick={() => setMode("qa")}>Q&A</button>
          <button className={`tab ${mode === "lecture" ? "active" : ""}`} onClick={() => setMode("lecture")}>Lectures</button>
        </div>

        {mode === "qa" ? (
          <div className="stack">
            <div className="card">
              <h3>Ask (upload WAV)</h3>
              <div className="stack">
                <input type="file" accept=".wav" onChange={(e)=>setQaFile(e.target.files?.[0] ?? null)} />
                <div className="row">
                  <button className="btn primary" onClick={sendQA}>Send</button>
                  <button className="btn ghost" onClick={()=>{setAudioUrl(null);setPhonemes(null);}}>Reset</button>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Now Playing</h3>
              <div className="stack" style={{fontSize:13, color:"var(--muted)"}}>
                <div>Audio: {audioUrl ? "yes" : "—"}</div>
                <div>Phonemes: {phonemes ? "yes" : "—"}</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="stack">
            <div className="card">
              <h3>Create Lecture</h3>
              <div className="stack">
                <textarea
                  placeholder="Paste the teacher's lesson text here…"
                  value={lectureText}
                  onChange={(e)=>setLectureText(e.target.value)}
                />
                <div className="row">
                  <button className="btn primary" onClick={createLectureFromText}>Summarize</button>
                  <button className="btn ghost" onClick={()=>setLectureText("")}>Clear</button>
                </div>
              </div>
            </div>

            {summary && (
              <div className="card">
                <h3>Summary</h3>
                <div style={{whiteSpace:"pre-wrap"}}>{summary}</div>
                <div className="row" style={{marginTop:10}}>
                  <button className="btn ok" onClick={speakSummary}>Speak Summary</button>
                  <button className="btn ghost" onClick={()=>{setSummary(""); setAudioUrl(null); setPhonemes(null);}}>Reset</button>
                </div>
              </div>
            )}

            <div className="card">
              <h3>Lectures</h3>
              <ul className="list">
                {lectures.map((lec)=>(
                  <li key={lec.id}>
                    <button
                      className="btn"
                      style={{width:"100%", textAlign:"left"}}
                      onClick={()=>openLecture(lec.id)}
                    >
                      <div style={{fontWeight:600}}>{lec.title}</div>
                      <div style={{fontSize:12, color:"var(--muted)"}}>{lec.subject || lec.id}</div>
                    </button>
                  </li>
                ))}
                {lectures.length === 0 && (
                  <li style={{color:"var(--muted)", fontSize:13}}>No lectures yet.</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </aside>

      {/* ---- Canvas ---- */}
      <main className="canvasWrap">
        <Canvas
          shadows
          camera={{ position: [0, 0, 8], fov: 42 }}
          gl={{ alpha: false }}
        >
          <Experience audioUrl={audioUrl} phonemes={phonemes} />
        </Canvas>
      </main>
    </div>
  );
}
