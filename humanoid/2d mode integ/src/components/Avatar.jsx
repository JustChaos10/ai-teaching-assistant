import React, { useEffect, useRef, useState } from 'react';
import { modelConfig, getModelPath, getModelSettings } from '../modelConfig';

export function Avatar({ audioUrl, phonemes = [] }) {
  const canvasRef = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(null);
  const modelRef = useRef(null);
  const animationFrameRef = useRef(null);

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
        
        // Load Cubism Framework modules
        const { CubismFramework: Framework, Option } = await import('../vendor/Framework/live2dcubismframework.js');
        const { CubismMatrix44 } = await import('../vendor/Framework/math/cubismmatrix44.js');
        const { CubismModelSettingJson } = await import('../vendor/Framework/cubismmodelsettingjson.js');
        const { CubismUserModel } = await import('../vendor/Framework/model/cubismusermodel.js');
        const { CubismRenderer_WebGL } = await import('../vendor/Framework/rendering/cubismrenderer_webgl.js');
        const { CubismPose } = await import('../vendor/Framework/effect/cubismpose.js');
        const { CubismBreath } = await import('../vendor/Framework/effect/cubismbreath.js');
        const { BreathParameterData } = await import('../vendor/Framework/effect/cubismbreath.js');
        const { csmVector } = await import('../vendor/Framework/type/csmvector.js');
        
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
          const { CubismPhysics } = await import('../vendor/Framework/physics/cubismphysics.js');
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
        
        // Apply model-specific scale and position from config
        projection.scale(modelSettings.scale, modelSettings.scale);
        projection.translateX(modelSettings.position.x);
        projection.translateY(modelSettings.position.y);
        
        renderer.setMvpMatrix(projection);
        
        modelRef.current = { gl, userModel, model, renderer, projection, CubismFramework, breath, pose, physics };
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
    
    const startAnimation = () => {
      let frameCount = 0;
      let lastTime = performance.now();
      let totalTime = 0;
      
      const animate = () => {
        if (!modelRef.current) return;
        
        const { gl, userModel, model, renderer, projection, breath, pose, physics } = modelRef.current;
        
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
            console.log(`Parameter ${i}:`, paramId, typeof paramId);
          }
        }
        
        // Load saved parameters
        model.loadParameters();
        
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
        
        // Save parameters state
        model.saveParameters();
        
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
    console.log('Audio/phonemes changed:', { audioUrl, phonemes });
  }, [audioUrl, phonemes]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <canvas 
        ref={canvasRef} 
        className="avatar-canvas"
        style={{
          width: '800px',
          height: '800px',
          border: '2px solid cyan',
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
