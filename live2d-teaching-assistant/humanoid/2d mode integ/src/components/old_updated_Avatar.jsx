// src/components/Avatar.jsx
import React, { useEffect, useRef, useState } from 'react';

const Avatar = ({ lipSyncParams = {} }) => { // Props for future lip-sync (e.g., mouthOpen value)
  const canvasRef = useRef(null);
  const [model, setModel] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    let animationId;
    let cubismModel;

    const initLive2D = async () => {
      try {
        // Dynamic import Framework ES modules from dist/ (Vite resolves /CubismSdkForWeb-5-r.4/Framework/dist)
        const {
          CubismModelSettingJson,
          CubismUserModel,
          CubismRenderer_WebGL,
          CubismMatrix44,
          Live2DCubismFramework,
          Option,
          CubismLogLevel,
          CubismUserAllocator,
        } = await import('/CubismSdkForWeb-5-r.4/Framework/dist/live2dcubismframework.js');

        // Init Framework (set log level, allocator)
        Live2DCubismFramework.startUp();
        Live2DCubismFramework.CubismLog.setLogLevel(CubismLogLevel.OFF); // Silent logs
        Option.setupRenderer(true); // WebGL
        Live2DCubismFramework.initialize();

        // Load Haru model setting
        const modelSetting = new CubismModelSettingJson('/live2d-demo/Resources/Haru/Haru.model3.json');
        const modelHomeDir = modelSetting.getModelDirPath();
        const userModel = CubismUserModel.createModel(modelSetting, modelHomeDir, '/live2d-demo/Resources/'); // Base path for assets

        // Load model
        await userModel.loadAssets(modelSetting);
        cubismModel = userModel.getModel();
        setModel(cubismModel);

        // Setup renderer (WebGL on canvas)
        const canvas = canvasRef.current;
        const gl = canvas.getContext('webgl');
        if (!gl) throw new Error('WebGL not supported');

        const renderer = CubismRenderer_WebGL.create(gl);
        renderer.setIsUsingHighPrecision(true);
        renderer.startUp();
        userModel.setRenderer(renderer);

        // View matrix (scale/position for 400x400 canvas)
        const viewMatrix = new CubismMatrix44();
        viewMatrix.scale(1, 1);
        viewMatrix.translate(-1, 1); // Center
        viewMatrix.scale(0.5, -0.5); // Fit

        setIsLoaded(true);

        // Animation loop
        const animate = () => {
          if (!cubismModel || !isLoaded) return;

          // Update model (time-based animation)
          cubismModel.update();
          cubismModel.draw(renderer);

          // Lip-sync placeholder: Update mouth param if provided
          if (lipSyncParams.mouthOpen !== undefined) {
            cubismModel.addParameterValueById('PARAM_MOUTH_OPEN_Y', lipSyncParams.mouthOpen, 1.0);
          }

          // Clear and render
          gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
          gl.clearColor(1.0, 1.0, 1.0, 1.0); // White bg
          renderer.setMvpMatrix(viewMatrix);
          renderer.doDrawModel(cubismModel, 0.5, 0.5); // Center draw

          animationId = requestAnimationFrame(animate);
        };
        animate();

      } catch (error) {
        console.error('Live2D Init Error:', error);
      }
    };

    initLive2D();

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (model) {
        model.delete();
        Live2DCubismFramework.dispose();
      }
    };
  }, [lipSyncParams]);

  if (!isLoaded) {
    return <div>Loading Haru Avatar...</div>;
  }

  return (
    <div style={{ width: '400px', height: '400px' }}>
      <canvas ref={canvasRef} width={400} height={400} style={{ border: '1px solid #ccc' }} />
    </div>
  );
};

export default Avatar;
