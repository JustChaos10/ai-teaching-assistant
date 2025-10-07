/*
Fully working Avatar with voice recording -> FastAPI /ask -> lip-sync playback
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
  // Load model and animations
  const gltf = useGLTF("/models/646d9dcdc8a5f5bddbfac913.glb");
  const { nodes, materials } = gltf;
  const idle = useFBX("/animations/Idle.fbx");
  const greet = useFBX("/animations/Standing Greeting.fbx");

  idle.animations[0].name = "Idle";
  greet.animations[0].name = "Greeting";

  const group = useRef();
  const { actions } = useAnimations(
    [idle.animations[0], greet.animations[0]],
    group
  );

  const [animation, setAnimation] = useState("Idle");
  const [recording, setRecording] = useState(false);
  const [audio, setAudio] = useState(null);
  const [phonemes, setPhonemes] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Animation control
  useEffect(() => {
    if (!actions || !actions[animation]) return;
    actions[animation].reset().fadeIn(0.5).play();
    return () => actions[animation]?.fadeOut(0.5);
  }, [animation, actions]);

  // Head follow camera
  useFrame((state) => {
    const head = group.current?.getObjectByName("Head");
    if (head) head.lookAt(state.camera.position);
  });

  // Mouth animation
  useFrame(() => {
    if (!phonemes || !audio || audio.paused) return;

    const currentTime = audio.currentTime;
    if (!nodes?.Wolf3D_Head || !nodes?.Wolf3D_Teeth) return;

    // Reset visemes
    Object.values(visemeMap).forEach((v) => {
      const hi = nodes.Wolf3D_Head.morphTargetDictionary[v];
      const ti = nodes.Wolf3D_Teeth.morphTargetDictionary[v];
      if (hi !== undefined) nodes.Wolf3D_Head.morphTargetInfluences[hi] = 0;
      if (ti !== undefined) nodes.Wolf3D_Teeth.morphTargetInfluences[ti] = 0;
    });

    // Apply current cue
    const cue = phonemes.mouthCues.find(
      (m) => currentTime >= m.start && currentTime <= m.end
    );
    if (cue) {
      const morph = visemeMap[cue.value];
      const hi = nodes.Wolf3D_Head.morphTargetDictionary[morph];
      const ti = nodes.Wolf3D_Teeth.morphTargetDictionary[morph];
      if (hi !== undefined)
        nodes.Wolf3D_Head.morphTargetInfluences[hi] = THREE.MathUtils.lerp(
          nodes.Wolf3D_Head.morphTargetInfluences[hi],
          1,
          0.5
        );
      if (ti !== undefined)
        nodes.Wolf3D_Teeth.morphTargetInfluences[ti] = THREE.MathUtils.lerp(
          nodes.Wolf3D_Teeth.morphTargetInfluences[ti],
          1,
          0.5
        );
    }
  });

  // --- 🎙️ Mic recording + backend upload ---
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
      console.log("🎙️ Recording started...");
    } catch (err) {
      console.error("Microphone error:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
      console.log("🛑 Recording stopped.");
    }
  };

  // Render model + UI
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

      {/* Record button */}
      <Html position={[0, 2, 0]}>
        <div style={{ textAlign: "center" }}>
          <button
            onClick={recording ? stopRecording : startRecording}
            style={{
              backgroundColor: recording ? "#ff4b4b" : "#4CAF50",
              color: "white",
              fontSize: "18px",
              border: "none",
              borderRadius: "10px",
              padding: "12px 25px",
              cursor: "pointer",
              boxShadow: "0px 0px 10px rgba(0,0,0,0.3)",
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
