/*
Avatar with:
- 🎙 Floating mic button (bottom center) → POST /ask → lip-sync playback
- 🧠 Supports external audioUrl + phonemes (lecture summary playback)
- 🧍 Stays on Idle while speaking (no greeting/wave loop)
*/

import { useAnimations, useFBX, useGLTF, Html } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

const visemeMap = {
  A: "viseme_PP",
  B: "viseme_kk",
  C: "viseme_I",
  D: "viseme_AA",
  E: "viseme_O",
  F: "viseme_U",
  G: "viseme_FF",
  H: "viseme_TH",
  X: "viseme_PP",
};

export function Avatar(props) {
  const { audioUrl: externalAudioUrl, phonemes: externalPhonemes } = props;

  // --- Model + Animations ---
  const gltf = useGLTF("/models/646d9dcdc8a5f5bddbfac913.glb");
  const { nodes, materials } = gltf;

  // keep only Idle to avoid waving
  const idle = useFBX("/animations/Idle.fbx");
  idle.animations[0].name = "Idle";

  const group = useRef();
  const { actions } = useAnimations([idle.animations[0]], group);

  // --- State ---
  const [animation, setAnimation] = useState("Idle");
  const [recording, setRecording] = useState(false);
  const [audio, setAudio] = useState(null);
  const [phonemes, setPhonemes] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // --- If parent pushes external audio (lecture mode) ---
  useEffect(() => {
    if (externalAudioUrl && externalPhonemes) {
      const extAudio = new Audio(externalAudioUrl);
      extAudio.crossOrigin = "anonymous";
      setPhonemes(externalPhonemes);
      setAudio(extAudio);
      setAnimation("Idle");        // ✅ keep idle while speaking
      extAudio.play();
      extAudio.onended = () => setAnimation("Idle");
    }
  }, [externalAudioUrl, externalPhonemes]);

  // --- Animation control ---
  useEffect(() => {
    if (!actions || !actions[animation]) return;
    actions[animation].reset().fadeIn(0.4).play();
    return () => actions[animation]?.fadeOut(0.3);
  }, [animation, actions]);

  // --- Subtle head follow ---
  useFrame((state) => {
    const head = group.current?.getObjectByName("Head");
    if (head) head.lookAt(state.camera.position);
  });

  // --- Lip-sync visemes ---
  useFrame(() => {
    if (!phonemes || !audio || audio.paused) return;
    const t = audio.currentTime;
    if (!nodes?.Wolf3D_Head || !nodes?.Wolf3D_Teeth) return;

    // reset
    Object.values(visemeMap).forEach((v) => {
      const hi = nodes.Wolf3D_Head.morphTargetDictionary[v];
      const ti = nodes.Wolf3D_Teeth.morphTargetDictionary[v];
      if (hi !== undefined) nodes.Wolf3D_Head.morphTargetInfluences[hi] = 0;
      if (ti !== undefined) nodes.Wolf3D_Teeth.morphTargetInfluences[ti] = 0;
    });

    // current cue
    const cue = phonemes.mouthCues.find((m) => t >= m.start && t <= m.end);
    if (cue) {
      const morph = visemeMap[cue.value];
      const hi = nodes.Wolf3D_Head.morphTargetDictionary[morph];
      const ti = nodes.Wolf3D_Teeth.morphTargetDictionary[morph];
      if (hi !== undefined)
        nodes.Wolf3D_Head.morphTargetInfluences[hi] = THREE.MathUtils.lerp(
          nodes.Wolf3D_Head.morphTargetInfluences[hi], 1, 0.55
        );
      if (ti !== undefined)
        nodes.Wolf3D_Teeth.morphTargetInfluences[ti] = THREE.MathUtils.lerp(
          nodes.Wolf3D_Teeth.morphTargetInfluences[ti], 1, 0.55
        );
    }
  });

  // --- 🎙 Mic → backend /ask ---
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

        setAnimation("Idle");

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
            setAnimation("Idle");  // ✅ keep idle while speaking
            audioEl.play();
            audioEl.onended = () => setAnimation("Idle");
          } else {
            console.error("Invalid backend response:", data);
          }
        } catch (err) {
          console.error("Backend request failed:", err);
        }
      };

      recorder.start();
      setRecording(true);
    } catch (err) {
      console.error("Microphone error:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <>
      <group {...props} ref={group} dispose={null}>
        <primitive object={nodes.Hips} />
        <skinnedMesh
          geometry={nodes.Wolf3D_Body.geometry}
          material={materials.Wolf3D_Body}
          skeleton={nodes.Wolf3D_Body.skeleton}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Outfit_Top.geometry}
          material={materials.Wolf3D_Outfit_Top}
          skeleton={nodes.Wolf3D_Outfit_Top.skeleton}
        />
        <skinnedMesh
          geometry={nodes.Wolf3D_Hair.geometry}
          material={materials.Wolf3D_Hair}
          skeleton={nodes.Wolf3D_Hair.skeleton}
        />
        <skinnedMesh
          name="EyeLeft"
          geometry={nodes.EyeLeft.geometry}
          material={materials.Wolf3D_Eye}
          skeleton={nodes.EyeLeft.skeleton}
          morphTargetDictionary={nodes.EyeLeft.morphTargetDictionary}
          morphTargetInfluences={nodes.EyeLeft.morphTargetInfluences}
        />
        <skinnedMesh
          name="EyeRight"
          geometry={nodes.EyeRight.geometry}
          material={materials.Wolf3D_Eye}
          skeleton={nodes.EyeRight.skeleton}
          morphTargetDictionary={nodes.EyeRight.morphTargetDictionary}
          morphTargetInfluences={nodes.EyeRight.morphTargetInfluences}
        />
        <skinnedMesh
          name="Wolf3D_Head"
          geometry={nodes.Wolf3D_Head.geometry}
          material={materials.Wolf3D_Skin}
          skeleton={nodes.Wolf3D_Head.skeleton}
          morphTargetDictionary={nodes.Wolf3D_Head.morphTargetDictionary}
          morphTargetInfluences={nodes.Wolf3D_Head.morphTargetInfluences}
        />
        <skinnedMesh
          name="Wolf3D_Teeth"
          geometry={nodes.Wolf3D_Teeth.geometry}
          material={materials.Wolf3D_Teeth}
          skeleton={nodes.Wolf3D_Teeth.skeleton}
          morphTargetDictionary={nodes.Wolf3D_Teeth.morphTargetDictionary}
          morphTargetInfluences={nodes.Wolf3D_Teeth.morphTargetInfluences}
        />
      </group>

      {/* Floating mic button (always available) */}
      <Html fullscreen>
        <div style={{
          position: "fixed",
          left: 0, right: 0, bottom: 24,
          display: "flex", justifyContent: "center", pointerEvents: "none"
        }}>
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
              boxShadow: "0px 8px 24px rgba(0,0,0,0.25)"
            }}
          >
            {recording ? "Stop Recording" : "Start Recording"}
          </button>
        </div>
      </Html>
    </>
  );
}

useGLTF.preload("/models/646d9dcdc8a5f5bddbfac913.glb");
