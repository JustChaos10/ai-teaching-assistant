import React, { useEffect, useRef, useState } from 'react';
import { modelConfig, getModelPath, getModelSettings } from '../modelConfig';
import { CubismFramework as CubismFrameworkLib, Option } from '../vendor/Framework/live2dcubismframework.js';
import { CubismMatrix44 } from '../vendor/Framework/math/cubismmatrix44.js';
import { CubismModelSettingJson } from '../vendor/Framework/cubismmodelsettingjson.js';
import { CubismUserModel } from '../vendor/Framework/model/cubismusermodel.js';
import { CubismPose } from '../vendor/Framework/effect/cubismpose.js';
import { CubismBreath, BreathParameterData } from '../vendor/Framework/effect/cubismbreath.js';
import { csmVector } from '../vendor/Framework/type/csmvector.js';
import { CubismPhysics } from '../vendor/Framework/physics/cubismphysics.js';
import { CubismMotion } from '../vendor/Framework/motion/cubismmotion.js';
import { CubismMotionManager } from '../vendor/Framework/motion/cubismmotionmanager.js';

export function Avatar({ audioUrl }) {
  const canvasRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(null);
  const modelRef = useRef(null);
  const animationFrameRef = useRef(null);
  const audioRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const lipSyncValueRef = useRef(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const motionsRef = useRef(new Map());
  const motionManagerRef = useRef(null);
  const eyeBlinkIdsRef = useRef([]);
  const lipSyncIdsRef = useRef([]);

  useEffect(() => {
    console.log('Avatar mounted, canvas:', canvasRef.current);
    
    if (!canvasRef.current) {
      console.error('Canvas ref is null');
      return;
    }

    const canvas = canvasRef.current;

    // Set canvas size with device pixel ratio for high-DPI displays
    const displayWidth = 800;
    const displayHeight = 800;
    const dpr = window.devicePixelRatio || 1;

    canvas.width = displayWidth * dpr;
    canvas.height = displayHeight * dpr;
    canvas.style.width = `${displayWidth}px`;
    canvas.style.height = `${displayHeight}px`;

    console.log(`Canvas initialized: ${canvas.width}x${canvas.height} (DPR: ${dpr})`);

    let gl = null;
    let CubismFramework = null;
    let userModel = null;
    
    const initLive2D = async () => {
      try {
        console.log('Initializing Live2D...');
        
        // Load Live2D Core dynamically
        const Live2DCubismCore = await new Promise((resolve, reject) => {
          if (window.Live2DCubismCore) {
            resolve(window.Live2DCubismCore);
            return;
          }
          const script = document.createElement('script');
          script.src = '/CubismSdkForWeb-5-r.4/Core/live2dcubismcore.js';
          script.onload = () => {
            console.log('Live2D Core loaded');
            resolve(window.Live2DCubismCore);
          };
          script.onerror = () => reject(new Error('Failed to load Live2D Core'));
          document.head.appendChild(script);
        });
        
        console.log('Live2DCubismCore available');
        
        // Use statically imported Cubism Framework modules
        const Framework = CubismFrameworkLib;
        CubismFramework = Framework;
        console.log('Framework modules loaded');
        
        // Initialize Framework
        const option = new Option();
        option.logFunction = console.log;
        option.loggingLevel = 0; // Verbose
        CubismFramework.startUp(option);
        CubismFramework.initialize();
        console.log('Framework initialized');
        
        // Get WebGL context
        gl = canvas.getContext('webgl', { 
          alpha: true, 
          premultipliedAlpha: true,
          antialias: true,
          preserveDrawingBuffer: true
        });
        
        if (!gl) {
          throw new Error('WebGL not supported');
        }
        
        // Set viewport to match canvas buffer size
        gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight);
        console.log(`WebGL viewport: ${gl.drawingBufferWidth}x${gl.drawingBufferHeight}`);
        
        console.log('WebGL context created');
        
        // Get model configuration
        const modelName = modelConfig.modelName;
        const modelPath = getModelPath();
        const modelSettings = getModelSettings();
        console.log(`Loading model: ${modelName} from ${modelPath}`);
        
        // Load model3.json
        const modelJsonResponse = await fetch(modelPath);
        const modelJsonArrayBuffer = await modelJsonResponse.arrayBuffer();
        console.log('Model JSON loaded');
        
        // Parse model settings
        const setting = new CubismModelSettingJson(modelJsonArrayBuffer, modelJsonArrayBuffer.byteLength);
        
        // Create user model
        userModel = new CubismUserModel();
        
        // Load MOC3
        const mocFileName = setting.getModelFileName();
        const mocResponse = await fetch(`${modelConfig.basePath}/${modelName}/${mocFileName}`);
        const mocArrayBuffer = await mocResponse.arrayBuffer();
        console.log('MOC3 file loaded, size:', mocArrayBuffer.byteLength);
        
        // Load model using the Framework's loadModel method
        userModel.loadModel(mocArrayBuffer, false);
        console.log('Model loaded into CubismUserModel');
        
        // Create renderer using userModel's method
        userModel.createRenderer();
        const renderer = userModel.getRenderer();
        console.log('Renderer created via userModel');
        
        // Get the actual model
        const model = userModel.getModel();
        console.log('Got model from userModel, parameter count:', model.getParameterCount());
        
        // Initialize renderer with model (critical for clipping masks)
        renderer.initialize(model);
        renderer.setIsPremultipliedAlpha(true);
        renderer.startUp(gl);
        console.log('Renderer initialized');
        
        // Load textures
        const textureCount = setting.getTextureCount();
        const usePremultiply = true; // iPhone alpha quality improvement
        
        for (let i = 0; i < textureCount; i++) {
          // Get texture filename from model settings (includes subdirectory like "Haru.2048/texture_00.png")
          const textureFileName = setting.getTextureFileName(i);
          const texturePath = `${modelConfig.basePath}/${modelName}/${textureFileName}`;
          console.log('Loading texture:', texturePath);
          
          const texture = gl.createTexture();
          const image = new Image();
          
          await new Promise((resolve, reject) => {
            image.onload = () => {
              // Bind texture
              gl.bindTexture(gl.TEXTURE_2D, texture);
              
              // Set texture parameters
              gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
              gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
              
              // Enable premultiplied alpha for better quality
              if (usePremultiply) {
                gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, 1);
              }
              
              // Upload texture data
              gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);
              
              // Generate mipmaps
              gl.generateMipmap(gl.TEXTURE_2D);
              
              // Unbind texture
              gl.bindTexture(gl.TEXTURE_2D, null);
              
              // Bind texture to renderer
              renderer.bindTexture(i, texture);
              console.log(`Texture ${i} (${textureFileName}) loaded and bound - Size: ${image.width}x${image.height}`);
              resolve();
            };
            image.onerror = (err) => {
              console.error(`Failed to load texture: ${texturePath}`, err);
              reject(err);
            };
            image.src = texturePath;
          });
        }
        
        // Set renderer to use premultiplied alpha
        renderer.setIsPremultipliedAlpha(usePremultiply);
        console.log('All textures loaded successfully');
        
        // Load physics if available
        let physics = null;
        if (setting.getPhysicsFileName() != '') {
          const physicsResponse = await fetch(`${modelConfig.basePath}/${modelName}/${setting.getPhysicsFileName()}`);
          const physicsBuffer = await physicsResponse.arrayBuffer();
          physics = CubismPhysics.create(physicsBuffer, physicsBuffer.byteLength);
          console.log('Physics loaded');
        }
        
        // Load pose data if available
        let pose = null;
        if (setting.getPoseFileName() != '') {
          const poseResponse = await fetch(`${modelConfig.basePath}/${modelName}/${setting.getPoseFileName()}`);
          const poseBuffer = await poseResponse.arrayBuffer();
          pose = CubismPose.create(poseBuffer, poseBuffer.byteLength);
          console.log('Pose loaded');
        }
        
        // Load motions and setup motion manager
        const motionManager = new CubismMotionManager();
        motionManagerRef.current = motionManager;
        
        // Setup eye blink and lip sync IDs
        const eyeBlinkIds = new csmVector();
        const lipSyncIds = new csmVector();
        
        // Get eye blink parameter IDs
        const eyeBlinkCount = setting.getEyeBlinkParameterCount();
        for (let i = 0; i < eyeBlinkCount; i++) {
          const paramId = setting.getEyeBlinkParameterId(i);
          if (paramId) {
            eyeBlinkIds.pushBack(paramId);
          }
        }
        
        // Get lip sync parameter IDs
        const lipSyncCount = setting.getLipSyncParameterCount();
        for (let i = 0; i < lipSyncCount; i++) {
          const paramId = setting.getLipSyncParameterId(i);
          if (paramId) {
            lipSyncIds.pushBack(paramId);
          }
        }
        
        eyeBlinkIdsRef.current = eyeBlinkIds;
        lipSyncIdsRef.current = lipSyncIds;
        
        console.log(`Eye blink IDs: ${eyeBlinkCount}, Lip sync IDs: ${lipSyncCount}`);
        
        // Preload all motions from all groups
        const motions = new Map();
        
        if (setting.isExistMotionGroups()) {
          const groupCount = setting.getMotionGroupCount();
          console.log(`Motion groups: ${groupCount}`);
          
          for (let groupIdx = 0; groupIdx < groupCount; groupIdx++) {
            const groupName = setting.getMotionGroupName(groupIdx);
            const motionCount = setting.getMotionCount(groupName);
            
            console.log(`Loading motion group "${groupName}" with ${motionCount} motions`);
            
            for (let i = 0; i < motionCount; i++) {
              try {
                const motionFileName = setting.getMotionFileName(groupName, i);
                const motionPath = `${modelConfig.basePath}/${modelName}/${motionFileName}`;
                
                const motionResponse = await fetch(motionPath);
                const motionBuffer = await motionResponse.arrayBuffer();
                const motion = CubismMotion.create(motionBuffer, motionBuffer.byteLength);
                
                // Set fade times from model settings or use defaults
                const fadeInTime = setting.getMotionFadeInTimeValue(groupName, i);
                const fadeOutTime = setting.getMotionFadeOutTimeValue(groupName, i);
                
                motion.setFadeInTime(fadeInTime >= 0 ? fadeInTime : 1.0);
                motion.setFadeOutTime(fadeOutTime >= 0 ? fadeOutTime : 1.0);
                
                // Set effect IDs for eye blink and lip sync
                motion.setEffectIds(eyeBlinkIds, lipSyncIds);
                
                // Store motion with key: "GroupName_index"
                const motionKey = `${groupName}_${i}`;
                motions.set(motionKey, motion);
                
                console.log(`Loaded motion: ${motionKey} (fadeIn: ${motion.getFadeInTime()}s, fadeOut: ${motion.getFadeOutTime()}s)`);
              } catch (e) {
                console.warn(`Failed to load motion ${groupName}_${i}:`, e);
              }
            }
          }
        } else {
          console.log('No motion groups defined in model settings');
        }
        
        console.log(`Total motions loaded: ${motions.size}`);
        motionsRef.current = motions;
        
        // Initialize model parameters to default values
        model.saveParameters();
        
        // Setup breathing animation
        const breath = CubismBreath.create();
        const breathParams = new csmVector();
        breathParams.pushBack(new BreathParameterData(CubismFramework.getIdManager().getId('ParamAngleX'), 0.0, 15.0, 6.5345, 0.5));
        breathParams.pushBack(new BreathParameterData(CubismFramework.getIdManager().getId('ParamAngleY'), 0.0, 8.0, 3.5345, 0.5));
        breathParams.pushBack(new BreathParameterData(CubismFramework.getIdManager().getId('ParamAngleZ'), 0.0, 10.0, 5.5345, 0.5));
        breathParams.pushBack(new BreathParameterData(CubismFramework.getIdManager().getId('ParamBodyAngleX'), 0.0, 4.0, 15.5345, 0.5));
        breathParams.pushBack(new BreathParameterData(CubismFramework.getIdManager().getId('ParamBreath'), 0.5, 0.5, 3.2345, 1.0));
        breath.setParameters(breathParams);
        console.log('Breath effect initialized');
        
        // Setup projection matrix
        const projection = new CubismMatrix44();
        projection.loadIdentity();

        const canvasWidth = canvas.width;
        const canvasHeight = canvas.height;

        if (canvasWidth > canvasHeight) {
          projection.scale(1.0, canvasWidth / canvasHeight);
        } else {
          projection.scale(canvasHeight / canvasWidth, 1.0);
        }

        // Scale the viewport to show more vertical space (zoom out vertically)
        projection.scale(1.0, 0.8);

        // Apply model-specific scale and position from config
        projection.scale(modelSettings.scale, modelSettings.scale);
        projection.translateX(modelSettings.position.x);
        projection.translateY(modelSettings.position.y);

        renderer.setMvpMatrix(projection);
        
        // Get the mouth parameter ID from lip sync settings (supports all models)
        let mouthParamId = null;
        if (lipSyncIds.getSize() > 0) {
          // Use the first lip sync parameter (usually the mouth)
          mouthParamId = lipSyncIds.at(0);
          console.log('Using lip sync parameter from model settings:', mouthParamId);
        } else {
          // Fallback to common parameter names
          console.warn('No lip sync parameters found in model settings, trying fallbacks');
          try {
            mouthParamId = CubismFramework.getIdManager().getId('ParamMouthOpenY');
          } catch (e) {
            try {
              mouthParamId = CubismFramework.getIdManager().getId('PARAM_MOUTH_OPEN_Y');
            } catch (e2) {
              console.error('Could not find mouth parameter');
            }
          }
        }
        console.log('Mouth parameter ID:', mouthParamId);
        
        modelRef.current = { gl, userModel, model, renderer, projection, CubismFramework, breath, pose, physics, mouthParamId, motionManager, setting };
        setIsLoaded(true);
        setError(null);
        console.log('Live2D model fully loaded!');
        
        // Start animation loop
        startAnimation();
        
      } catch (err) {
        console.error('Live2D initialization error:', err);
        setError(err.message);
      }
    };
    
    const startRandomIdleMotion = () => {
      if (!modelRef.current) return;
      
      const { setting } = modelRef.current;
      const motionManager = motionManagerRef.current;
      const motions = motionsRef.current;
      
      if (!motionManager || !setting || motions.size === 0) {
        return;
      }
      
      // Get idle motion count
      const idleCount = setting.getMotionCount('Idle');
      if (idleCount === 0) {
        return;
      }
      
      // Pick random idle motion
      const randomIndex = Math.floor(Math.random() * idleCount);
      const motionKey = `Idle_${randomIndex}`;
      const motion = motions.get(motionKey);
      
      if (!motion) {
        console.warn(`Motion ${motionKey} not found`);
        return;
      }
      
      console.log(`Starting random idle motion: ${motionKey}`);
      motionManager.startMotionPriority(motion, false, 1);
    };
    
    const startAnimation = () => {
      let frameCount = 0;
      let lastTime = performance.now();
      let totalTime = 0;
      let currentMotionTime = 0;
      
      const animate = () => {
        if (!modelRef.current) return;
        
        const { gl, userModel, model, renderer, projection, breath, pose, physics, mouthParamId } = modelRef.current;
        
        // Calculate delta time
        const now = performance.now();
        const deltaTime = (now - lastTime) / 1000.0;
        lastTime = now;
        totalTime += deltaTime;
        
        // Clear canvas
        gl.clearColor(0.0, 0.0, 0.0, 0.0);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
        gl.clearDepth(1.0);
        
        // Enable blending
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
        
        // Log once
        if (frameCount === 0) {
          console.log('Starting render loop');
          console.log('Model parameter count:', model.getParameterCount());
          
          // Log all parameter IDs to see their format
          for (let i = 0; i < model.getParameterCount(); i++) {
            const paramId = model.getParameterId(i);
            const paramIdStr = String(paramId);
            console.log(`Parameter ${i}:`, paramIdStr, typeof paramId);
          }
        }
        
        // Apply audio-based lip sync BEFORE loading saved parameters
        if (analyserRef.current && audioRef.current && !audioRef.current.paused) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteFrequencyData(dataArray);
          
          // Calculate average volume
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
          }
          const average = sum / dataArray.length;
          
          // Normalize to 0-1 range and smooth
          const targetValue = Math.min(average / 60, 1.2); // More sensitive
          lipSyncValueRef.current += (targetValue - lipSyncValueRef.current) * 0.6;
          
          if (frameCount % 30 === 0) {
            console.log('Audio average:', average, 'Lip sync value:', lipSyncValueRef.current);
          }
        } else {
          // Reset mouth when not speaking
          lipSyncValueRef.current *= 0.85;
        }
        
        // Load saved parameters
        model.loadParameters();
        
        // Update motions through motion manager - MIMIC TYPESCRIPT SAMPLE
        if (motionManagerRef.current) {
          // Check if motion is finished, if so start a random idle motion
          if (motionManagerRef.current.isFinished()) {
            // Start random idle motion (priority 1 = idle priority)
            startRandomIdleMotion();
          } else {
            // Update current motion
            motionManagerRef.current.updateMotion(model, deltaTime);
          }
        }
        
        // Save parameters state
        model.saveParameters();
        
        // Apply physics
        if (physics) {
          physics.evaluate(model, deltaTime);
        }
        
        // Apply breathing animation
        if (breath) {
          breath.updateParameters(model, deltaTime);
        }
        
        // Apply pose
        if (pose) {
          pose.updateParameters(model, deltaTime);
        }
        
        // NOW apply lip sync - AFTER other animations
        if (mouthParamId) {
          model.setParameterValueById(mouthParamId, lipSyncValueRef.current);
          
          if (frameCount % 60 === 0) {
            console.log('Setting mouth to:', lipSyncValueRef.current);
          }
        }
        
        // Update model (required before drawing)
        model.update();
        
        // Set render state with proper viewport
        const viewport = [0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight];
        renderer.setRenderState(gl.getParameter(gl.FRAMEBUFFER_BINDING), viewport);
        
        // Draw model
        renderer.setMvpMatrix(projection);
        renderer.drawModel();
        
        frameCount++;
        animationFrameRef.current = requestAnimationFrame(animate);
      };
      
      animate();
    };
    
    initLive2D();

    return () => {
      // Cleanup
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      // Stop audio if playing
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      // Close audio context
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }

      if (modelRef.current) {
        const { userModel, renderer, CubismFramework } = modelRef.current;

        if (renderer) renderer.release();
        if (userModel) userModel.deleteModel();

        if (CubismFramework) {
          CubismFramework.dispose();
        }
      }
    };
  }, []);

  useEffect(() => {
    console.log('Audio changed:', { audioUrl });
    
    // Play audio when audioUrl is provided
    if (audioUrl) {
      console.log('Creating and playing audio from URL:', audioUrl);
      
      // Stop previous audio if playing
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      
      // Create new audio element
      const audio = new Audio(audioUrl);
      audio.crossOrigin = "anonymous";
      audioRef.current = audio;
      
      // Setup Web Audio API for lip sync
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      
      const audioContext = audioContextRef.current;
      const source = audioContext.createMediaElementSource(audio);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      
      // Connect: source -> analyser -> destination
      source.connect(analyser);
      analyser.connect(audioContext.destination);
      
      // Set speaking state
      setIsSpeaking(true);
      
      // Play the audio
      audio.play().catch(err => {
        console.error('Audio playback failed:', err);
      });
      
      // Clean up when audio ends
      audio.onended = () => {
        console.log('Audio playback finished');
        lipSyncValueRef.current = 0;
        audioRef.current = null;
        setIsSpeaking(false);
      };
    } else {
      // Reset lip sync when no audio
      lipSyncValueRef.current = 0;
      setIsSpeaking(false);
    }
  }, [audioUrl]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <canvas
        ref={canvasRef}
        className="avatar-canvas"
        style={{
          width: 'auto',
          height: '98vh',
          maxHeight: '100%',
          display: 'block'
        }}
      />
      <div style={{
        position: 'absolute',
        top: 10,
        left: 10,
        background: 'rgba(0,0,0,0.7)',
        color: 'white',
        padding: '10px',
        fontSize: '12px',
        fontFamily: 'monospace'
      }}>
        <div>Canvas Loaded: {canvasRef.current ? 'Yes' : 'No'}</div>
        <div>Model Loaded: {isLoaded ? 'Yes' : 'No'}</div>
        {error && <div style={{ color: 'red' }}>Error: {error}</div>}
      </div>
    </div>
  );
}
