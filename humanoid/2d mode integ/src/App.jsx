import { useEffect, useState, useRef } from "react";
import { API_BASE } from "./config";
import { Avatar } from './components/Avatar';

export default function App() {
  const [mode, setMode] = useState("qa"); // "qa" | "lecture" | "games"

  // shared state to drive Avatar
  const [audioUrl, setAudioUrl] = useState(null);
  const [images, setImages] = useState([]); // Generated educational images
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // State to store last successful response for replay
  const [lastResponse, setLastResponse] = useState(null);

  // ---- Q&A (record) ----
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const abortControllerRef = useRef(null);

  const startRecording = async () => {
    setAudioUrl(null);
    setImages([]); // Clear previous images
    setCurrentImageIndex(0);
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

        // Create AbortController for this request
        abortControllerRef.current = new AbortController();

        try {
          const res = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            body: formData,
            signal: abortControllerRef.current.signal,
          });
          const data = await res.json();

          if (data.audio_url) {
            const audioUrlFull = `${API_BASE}${data.audio_url}`;
            setAudioUrl(audioUrlFull);

            // Handle images if returned
            const imagesData = data.images && data.images.length > 0 ? data.images : [];
            if (imagesData.length > 0) {
              console.log(`Received ${imagesData.length} images from backend`);
              setImages(imagesData);
              setCurrentImageIndex(0);

              // Start dynamic timed image display
              startImageSlideshow(imagesData);
            }

            // Store last successful response for replay
            setLastResponse({
              audioUrl: audioUrlFull,
              images: imagesData
            });
          } else {
            console.error("Invalid backend response:", data);
            alert("Sorry, I couldn't process that. " + (data.error || ""));
          }
        } catch (err) {
          if (err.name === 'AbortError') {
            console.log("Request was cancelled by user");
          } else {
            console.error("Backend request failed:", err);
            alert("Sorry, something went wrong with the request.");
          }
        } finally {
          setProcessing(false);
          abortControllerRef.current = null;
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

  const cancelProcessing = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setProcessing(false);
      abortControllerRef.current = null;
      // Clear last response when cancelled so replay is disabled
      setLastResponse(null);
    }
  };

  const replayLastResponse = () => {
    if (!lastResponse) return;

    // Clear current slideshow timers
    if (slideshowTimerRef.current) {
      clearInterval(slideshowTimerRef.current);
    }
    imageTimersRef.current.forEach(timer => clearTimeout(timer));
    imageTimersRef.current = [];

    // Force audio replay by clearing first, then setting
    setAudioUrl(null);
    setTimeout(() => {
      setAudioUrl(lastResponse.audioUrl);
    }, 50);

    // Replay images if any
    if (lastResponse.images && lastResponse.images.length > 0) {
      setImages(lastResponse.images);
      setCurrentImageIndex(0);
      startImageSlideshow(lastResponse.images);
    } else {
      setImages([]);
      setCurrentImageIndex(0);
    }
  };

  // Image slideshow management with LLM-calculated timing
  const slideshowTimerRef = useRef(null);
  const imageTimersRef = useRef([]);
  
  const startImageSlideshow = (imagesData) => {
    // Clear existing timers
    if (slideshowTimerRef.current) {
      clearInterval(slideshowTimerRef.current);
    }
    imageTimersRef.current.forEach(timer => clearTimeout(timer));
    imageTimersRef.current = [];
    
    // Set up timed image display based on LLM-calculated start_time and duration
    imagesData.forEach((img, index) => {
      const startTime = img.start_time || 0;
      const duration = img.duration || 3;
      
      // Show image at start_time
      const showTimer = setTimeout(() => {
        console.log(`[${startTime}s] Showing image ${index + 1}: ${img.description} (for ${duration}s)`);
        setCurrentImageIndex(index);
      }, startTime * 1000);
      
      imageTimersRef.current.push(showTimer);
    });
  };
  
  useEffect(() => {
    return () => {
      if (slideshowTimerRef.current) {
        clearInterval(slideshowTimerRef.current);
      }
      imageTimersRef.current.forEach(timer => clearTimeout(timer));
    };
  }, []);


  // ---- Lectures ----
  const [lectures, setLectures] = useState([]);
  const [summary, setSummary] = useState("");
  const [fullContent, setFullContent] = useState("");
  const [lectureText, setLectureText] = useState("");
  const [selectedLectureId, setSelectedLectureId] = useState(null);

  async function loadLectures() {
    try {
      const r = await fetch(`${API_BASE}/lectures`);
      const data = await r.json();
      setLectures(Array.isArray(data) ? data : []);
    } catch (e) { console.error(e); }
  }
  useEffect(() => { loadLectures(); }, []);

  async function createLectureFromText() {
    if (!lectureText.trim()) return;
    const r = await fetch(`${API_BASE}/lectures`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "New Lecture", subject: "Math", content: lectureText }),
    });
    const data = await r.json();
    setSummary(data.summary || "");
    setFullContent(data.content || "");
    await loadLectures();
  }

  async function openLecture(id) {
    setSelectedLectureId(id);
    const r = await fetch(`${API_BASE}/lectures/${id}`);
    const data = await r.json();
    setSummary(data.summary || "");
    setFullContent(data.content || "");
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
                  <button className="btn ghost" onClick={() => { setAudioUrl(null); }}>Reset</button>
                </div>
              </div>
            </div>

            <div className="card">
              <h3>Now Playing</h3>
              <div className="stack" style={{ fontSize: 13, color: "var(--muted)" }}>
                <div>Audio: {audioUrl ? "yes" : "—"}</div>
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
            {summary && (
              <div className="card">
                <h3>Grade 1 Summary</h3>
                <div style={{
                  whiteSpace: "pre-wrap",
                  maxHeight: "400px",
                  overflowY: "auto",
                  padding: "10px",
                  border: "1px solid var(--stroke)",
                  borderRadius: "8px",
                  marginBottom: "10px"
                }}>{summary}</div>
                <div className="row" style={{ marginTop: 10 }}>
                  <button className="btn ok" onClick={speakSummary}>Speak Summary</button>
                  <button className="btn ghost" onClick={() => { setSummary(""); setFullContent(""); setAudioUrl(null); }}>Reset</button>
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
                  <li style={{ color: "var(--muted)", fontSize: 13 }}>No lectures yet. Create lectures at http://localhost:5000/teacher</li>
                )}
              </ul>
            </div>
          </div>
        )}
      </aside>

      {/* ---- Avatar Area (Live2D Canvas) ---- */}
      <main className="canvasWrap" style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundImage: 'url(/blackboard.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}>
        <Avatar audioUrl={audioUrl} />

        {/* Replay Button - Bottom Left */}
        <button
          onClick={replayLastResponse}
          disabled={!lastResponse}
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            padding: '14px 24px',
            fontSize: '16px',
            fontWeight: '600',
            color: lastResponse ? 'white' : '#666',
            background: lastResponse
              ? 'linear-gradient(180deg, #28c76f, #20a95e)'
              : 'rgba(255, 255, 255, 0.1)',
            border: lastResponse ? '1px solid #1c8f51' : '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '10px',
            cursor: lastResponse ? 'pointer' : 'not-allowed',
            transition: 'transform 0.1s ease, opacity 0.2s ease',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 50,
            opacity: lastResponse ? 1 : 0.5
          }}
          onMouseEnter={(e) => {
            if (lastResponse) e.target.style.transform = 'scale(1.05)';
          }}
          onMouseLeave={(e) => {
            if (lastResponse) e.target.style.transform = 'scale(1)';
          }}
        >
          <span style={{ fontSize: '20px' }}>🔄</span>
          Replay
        </button>
        
        {/* Educational Images Display */}
        {images.length > 0 && (
          <div style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            width: '400px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            zIndex: 100
          }}>
            <img 
              src={`${API_BASE}${images[currentImageIndex].url}`}
              alt={images[currentImageIndex].description}
              style={{
                width: '100%',
                height: 'auto',
                borderRadius: '8px',
                marginBottom: '12px'
              }}
            />
            <div style={{
              textAlign: 'center',
              fontSize: '16px',
              fontWeight: '600',
              color: '#333',
              marginBottom: '8px'
            }}>
              {images[currentImageIndex].description}
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '8px',
              marginTop: '12px'
            }}>
              {images.map((_, idx) => (
                <div
                  key={idx}
                  style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: idx === currentImageIndex ? '#4CAF50' : '#ddd',
                    transition: 'background 0.3s'
                  }}
                />
              ))}
            </div>
            <div style={{
              textAlign: 'center',
              fontSize: '12px',
              color: '#666',
              marginTop: '8px'
            }}>
              Step {currentImageIndex + 1} of {images.length}
            </div>
          </div>
        )}
        
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
            <button
              onClick={cancelProcessing}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '600',
                color: 'white',
                background: 'linear-gradient(180deg, #ff4b4b, #d13a3a)',
                border: '1px solid #a72a2a',
                borderRadius: '10px',
                cursor: 'pointer',
                transition: 'transform 0.1s ease, opacity 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.transform = 'scale(1.05)'}
              onMouseLeave={(e) => e.target.style.transform = 'scale(1)'}
            >
              Cancel
            </button>
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
