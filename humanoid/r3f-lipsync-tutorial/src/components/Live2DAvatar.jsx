/*
Live2D Avatar with:
- 🎙 Floating mic button → POST /ask → lip-sync playback
- 🧠 Supports external audioUrl + phonemes (lecture summary playback)
- 🎨 Uses Live2D Shizuka model
*/

import React, { useEffect, useRef, useState } from "react";
import * as PIXI from "pixi.js";
import { Live2DModel } from "@pixi/live2d-display";

// Enable Live2D logging for debugging
window.PIXI = PIXI;

// Phoneme to Live2D parameter mapping
const phonemeToLive2D = {
  A: { ParamMouthOpenY: 1.0 },
  B: { ParamMouthOpenY: 0.3, ParamMouthForm: -1.0 },
  C: { ParamMouthOpenY: 0.5, ParamMouthForm: 0.5 },
  D: { ParamMouthOpenY: 0.9, ParamMouthForm: 0.3 },
  E: { ParamMouthOpenY: 0.6, ParamMouthForm: 0.0 },
  F: { ParamMouthOpenY: 0.2, ParamMouthForm: -0.5 },
  G: { ParamMouthOpenY: 0.3, ParamMouthForm: -0.8 },
  H: { ParamMouthOpenY: 0.4, ParamMouthForm: 0.2 },
  X: { ParamMouthOpenY: 0.0 },
};

export function Live2DAvatar({ audioUrl: externalAudioUrl, phonemes: externalPhonemes }) {
  const canvasRef = useRef(null);
  const appRef = useRef(null);
  const modelRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [audio, setAudio] = useState(null);
  const [phonemes, setPhonemes] = useState(null);
  const animationFrameRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Initialize PIXI Application and Load Live2D Model
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Create PIXI application
    const app = new PIXI.Application({
      view: canvas,
      width: window.innerWidth,
      height: window.innerHeight,
      backgroundColor: 0xffffff,
      autoStart: true,
      antialias: true,
    });

    appRef.current = app;

    // Load Live2D model
    const loadModel = async () => {
      try {
        // Load Shizuka model (user needs to provide the model files)
        const model = await Live2DModel.from("/live2d-models/shizuku/shizuku.model.json", {
          autoInteract: false,
        });

        modelRef.current = model;

        // Scale and position the model
        const scaleX = (app.screen.width * 0.8) / model.width;
        const scaleY = (app.screen.height * 0.9) / model.height;
        const scale = Math.min(scaleX, scaleY);

        model.scale.set(scale);
        model.x = app.screen.width / 2;
        model.y = app.screen.height / 2;
        model.anchor.set(0.5, 0.5);

        // Add model to stage
        app.stage.addChild(model);

        // Start animation loop for lip-sync
        startLipSync();
      } catch (error) {
        console.error("Failed to load Live2D model:", error);
        console.log("Please ensure the Shizuka model is placed in /public/live2d-models/shizuku/");
      }
    };

    loadModel();

    // Handle window resize
    const handleResize = () => {
      app.renderer.resize(window.innerWidth, window.innerHeight);
      if (modelRef.current) {
        const model = modelRef.current;
        model.x = window.innerWidth / 2;
        model.y = window.innerHeight / 2;
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      app.destroy(true, { children: true, texture: true, baseTexture: true });
    };
  }, []);

  // Handle external audio/phonemes (from lecture mode)
  useEffect(() => {
    if (externalAudioUrl && externalPhonemes) {
      const extAudio = new Audio(externalAudioUrl);
      extAudio.crossOrigin = "anonymous";
      setPhonemes(externalPhonemes);
      setAudio(extAudio);
      extAudio.play();
      extAudio.onended = () => {
        setAudio(null);
        setPhonemes(null);
      };
    }
  }, [externalAudioUrl, externalPhonemes]);

  // Lip-sync animation loop
  const startLipSync = () => {
    const animate = () => {
      if (audio && !audio.paused && phonemes && modelRef.current) {
        const currentTime = audio.currentTime;

        // Find current phoneme cue
        const cue = phonemes.mouthCues?.find(
          (m) => currentTime >= m.start && currentTime <= m.end
        );

        if (cue && phonemeToLive2D[cue.value]) {
          const params = phonemeToLive2D[cue.value];

          // Apply parameters to Live2D model
          Object.entries(params).forEach(([paramName, value]) => {
            const paramIndex = modelRef.current.internalModel.coreModel.getParamIndex(
              `PARAM_${paramName.replace("Param", "").toUpperCase()}`
            );
            if (paramIndex >= 0) {
              modelRef.current.internalModel.coreModel.setParamFloat(paramIndex, value);
            }
          });
        } else {
          // Reset to idle mouth position
          const paramIndex = modelRef.current.internalModel.coreModel.getParamIndex(
            "PARAM_MOUTH_OPEN_Y"
          );
          if (paramIndex >= 0) {
            modelRef.current.internalModel.coreModel.setParamFloat(paramIndex, 0.0);
          }
        }
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();
  };

  // 🎙 Mic → backend /ask
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      audioChunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("file", blob, "input.wav");

        try {
          const res = await fetch("http://127.0.0.1:8000/ask", {
            method: "POST",
            body: formData,
          });
          const data = await res.json();

          if (data.audio_url && data.phonemes) {
            const audioEl = new Audio(`http://127.0.0.1:8000${data.audio_url}`);
            audioEl.crossOrigin = "anonymous";
            setAudio(audioEl);
            setPhonemes(data.phonemes);
            audioEl.play();
            audioEl.onended = () => {
              setAudio(null);
              setPhonemes(null);
            };
          } else {
            console.error("Invalid backend response:", data);
          }
        } catch (err) {
          console.error("Backend request failed:", err);
        }

        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone error:", err);
      alert("Failed to access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <canvas
        ref={canvasRef}
        style={{
          display: "block",
          width: "100%",
          height: "100%",
        }}
      />

      {/* Floating mic button */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 24,
          display: "flex",
          justifyContent: "center",
          pointerEvents: "none",
        }}
      >
        <button
          onClick={recording ? stopRecording : startRecording}
          style={{
            pointerEvents: "auto",
            backgroundColor: recording ? "#ff4b4b" : "#2ecc71",
            color: "white",
            fontSize: 16,
            border: "none",
            borderRadius: 12,
            padding: "12px 22px",
            boxShadow: "0px 8px 24px rgba(0,0,0,0.25)",
            cursor: "pointer",
            fontWeight: "600",
          }}
        >
          {recording ? "🔴 Stop Recording" : "🎙️ Start Recording"}
        </button>
      </div>
    </div>
  );
}
