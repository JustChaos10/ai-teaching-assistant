import { useEffect, useState, useRef } from "react";
import { API_BASE } from "./config";
import { Avatar } from './components/Avatar';

export default function App() {
  const [mode, setMode] = useState("qa"); // "qa" | "lecture" | "games"

  // shared state to drive Avatar (kept for future Live2D lip-sync)
  const [audioUrl, setAudioUrl] = useState(null);
  const [phonemes, setPhonemes] = useState(null);

  // ---- Q&A (record) ----
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    setAudioUrl(null);
    setPhonemes(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        setProcessing(true);
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("file", blob, "input.wav");

        try {
          const res = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            body: formData,
          });
          const data = await res.json();

          if (data.audio_url && data.phonemes) {
            setAudioUrl(`${API_BASE}${data.audio_url}`);
            setPhonemes(data.phonemes);
          } else {
            console.error("Invalid backend response:", data);
            alert("Sorry, I couldn't process that. " + (data.error || ""));
          }
        } catch (err) {
          console.error("Backend request failed:", err);
          alert("Sorry, something went wrong with the request.");
        } finally {
          setProcessing(false);
        }
      };

      recorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone error:", err);
      alert("Could not access the microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };


  // ---- Lectures ----
  const [lectures, setLectures] = useState([]);
  const [summary, setSummary] = useState("");
  const [lectureText, setLectureText] = useState("");
  const [selectedLectureId, setSelectedLectureId] = useState(null);

  async function loadLectures() {
    try {
      const r = await fetch(`${API_BASE}/lectures`);
      const data = await r.json();
      setLectures(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); }
  }
  useEffect(() => { /* loadLectures(); */ }, []);

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
    setProcessing(true);
    try {
      const r = await fetch(`${API_BASE}/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: summary }),
      });
      const data = await r.json();
      if (data.error) return alert(data.error);
      setAudioUrl(`${API_BASE}${data.audio_url}`);
      setPhonemes(data.phonemes);
    } finally {
      setProcessing(false);
    }
  }

  // ---- Games ----
  async function launchGames() {
    try {
      const r = await fetch(`${API_BASE}/launch-games`, { method: "POST" });
      const data = await r.json();
      if (data.error) return alert(data.error);
      alert("Games launcher opened! Check your desktop for the game window.");
    } catch (e) {
      alert("Failed to launch games: " + e.message);
    }
  }

  async function launchGameCreator() {
    try {
      const r = await fetch(`${API_BASE}/create-games`, { method: "POST" });
      const data = await r.json();
      if (data.error) return alert(data.error);
      alert("Game Creator opened! Check your desktop for the creator window.");
    } catch (e) {
      alert("Failed to launch game creator: " + e.message);
    }
  }

  return (
    <div className="app" style={{ background: '#0b1020', color: '#e9eef7' }}> {/* Force dark bg/light text */}
      {/* ---- Sidebar ---- */}
      <aside className="sidebar">
        <h1 className="h1">Teaching Assistant <span className="badge">beta</span></h1>

        <div className="tabs">
          <button className={`tab ${mode === "qa" ? "active" : ""}`} onClick={() => setMode("qa")}>Q&A</button>
          <button className={`tab ${mode === "lecture" ? "active" : ""}`} onClick={() => setMode("lecture")}>Lectures</button>
          <button className={`tab ${mode === "games" ? "active" : ""}`} onClick={() => setMode("games")}>Games</button>
        </div>

        {mode === "qa" ? (
          <div className="stack">
            <div className="card">
              <h3>Ask (Record Audio)</h3>
              <div className="stack">
                <button 
                  className={`btn ${recording ? 'danger' : 'ok'}`}
                  onClick={recording ? stopRecording : startRecording}
                >
                  {recording ? "Stop Recording" : "Start Recording"}
                </button>
                <div className="row">
                  <button className="btn ghost" onClick={() => { setAudioUrl(null); setPhonemes(null); }}>Reset</button>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Now Playing</h3>
              <div className="stack" style={{ fontSize: 13, color: "var(--muted)" }}>
                <div>Audio: {audioUrl ? "yes" : "—"}</div>
                <div>Phonemes: {phonemes ? "yes" : "—"}</div>
              </div>
            </div>
          </div>
        ) : mode === "games" ? (
          <div className="stack">
            <div className="card">
              <h3>🎮 Interactive Games</h3>
              <p style={{ color: "var(--muted)", marginBottom: 16 }}>
                Launch fun educational games for Grade 1 students!
              </p>
              <button 
                className="btn primary" 
                onClick={launchGames} 
                style={{ width: "100%", padding: "16px", fontSize: "18px", marginBottom: "12px" }}
              >
                🎲 Launch Games
              </button>
              <button 
                className="btn ok" 
                onClick={launchGameCreator} 
                style={{ width: "100%", padding: "16px", fontSize: "18px" }}
              >
                🎨 Create Games
              </button>
            </div>

            <div className="card">
              <h3>Available Games</h3>
              <ul style={{ listStyle: "none", padding: 0, color: "var(--muted)", fontSize: 14 }}>
                <li>🖐 Finger Counting</li>
                <li>🥗 Healthy vs Junk Food</li>
                <li>🧩 Puzzle Games</li>
                <li>📚 And more...</li>
              </ul>
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
                  onChange={(e) => setLectureText(e.target.value)}
                />
                <div className="row">
                  <button className="btn primary" onClick={createLectureFromText}>Summarize</button>
                  <button className="btn ghost" onClick={() => setLectureText("")}>Clear</button>
                </div>
              </div>
            </div>

            {summary && (
              <div className="card">
                <h3>Summary</h3>
                <div style={{ whiteSpace: "pre-wrap" }}>{summary}</div>
                <div className="row" style={{ marginTop: 10 }}>
                  <button className="btn ok" onClick={speakSummary}>Speak Summary</button>
                  <button className="btn ghost" onClick={() => { setSummary(""); setAudioUrl(null); setPhonemes(null); }}>Reset</button>
                </div>
              </div>
            )}

            <div className="card">
              <h3>Lectures</h3>
              <ul className="list">
                {lectures.map((lec) => (
                  <li key={lec.id}>
                    <button
                      className="btn"
                      style={{ width: "100%", textAlign: "left" }}
                      onClick={() => openLecture(lec.id)}
                    >
                      <div style={{ fontWeight: 600 }}>{lec.title}</div>
                      <div style={{ fontSize: 12, color: "var(--muted)" }}>{lec.subject || lec.id}</div>
                    </button>
                  </li>
                ))}
                {lectures.length === 0 && (
                  <li style={{ color: "var(--muted)", fontSize: 13 }}>No lectures yet.</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </aside>

      {/* ---- Avatar Area (Live2D Canvas) ---- */}
      <main className="canvasWrap" style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0b1020' }}>
        <Avatar audioUrl={audioUrl} phonemes={phonemes} />
        
        {/* Processing Overlay */}
        {processing && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            gap: '20px'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              border: '4px solid rgba(255, 255, 255, 0.3)',
              borderTop: '4px solid white',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
            <div style={{
              color: 'white',
              fontSize: '18px',
              fontWeight: '500'
            }}>
              Processing...
            </div>
          </div>
        )}
      </main>
      
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
