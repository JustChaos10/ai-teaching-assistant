import React, { useEffect, useRef, useState } from 'react';
import '../vendor/Core/live2dcubismcore.js';

export function Avatar({ audioUrl, phonemes = [] }) {
  const canvasRef = useRef(null);
  const modelRef = useRef(null);
  const animationFrame = useRef(null);
  const mouthTimer = useRef(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    let userModel, renderer, viewMatrix, Live2DCubismFramework;

          const initLive2D = async () => {
          try {
            const cubismModule = await import('@cubism/live2dcubismframework');
            console.log('ESM Framework loaded:', cubismModule ? 'Success (bundled)' : 'Failed');        Live2DCubismFramework = cubismModule.CubismFramework;
        if (!Live2DCubismFramework?.startUp) {
          throw new Error('Framework resolve failed—check src/vendor/Framework full copy (effect/ JS) and vite.config alias');
        }

        const {
          CubismModelSettingJson, CubismUserModel, CubismRenderer_WebGL, CubismMatrix44, Option,
          CubismLogLevel, CubismExpressionManager, CubismPhysics, CubismPose, CubismId
        } = cubismModule;

        Live2DCubismFramework.startUp();
        Live2DCubismFramework.CubismLog.setLogLevel(CubismLogLevel.OFF);
        Live2DCubismFramework.initialize();

        const canvas = canvasRef.current;
        if (!canvas) return;
        const gl = canvas.getContext('webgl');
        if (!gl) throw new Error('WebGL not supported');
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

        const modelSettingPath = '/live2d-demo/Resources/Haru/Haru.model3.json';
        const modelSetting = new CubismModelSettingJson(modelSettingPath);
        const modelHomeDir = '/live2d-demo/Resources/Haru/';

        console.log('Model refs:', {
          moc: modelSetting.getModelFileName(),
          textures: modelSetting.getTextureFileNames(),
          physics: modelSetting.getPhysicsFileName(),
          expressions: modelSetting.getExpressionFileNames(),
          pose: modelSetting.getPoseFileName()
        });

        userModel = CubismUserModel.createModel(modelSetting, modelHomeDir, '/live2d-demo/Resources/');
        await userModel.loadAssets(modelSetting);
        modelRef.current = userModel.getModel();

        if (!modelRef.current) {
          throw new Error('Model failed—check public/live2d-demo/Resources/Haru assets (moc3, textures) via Network');
        }

        try {
          CubismExpressionManager.create(modelRef.current);
          if (modelSetting.getPhysicsFileName()) CubismPhysics.create(modelRef.current);
          if (modelSetting.getPoseFileName()) CubismPose.create(modelRef.current);
        } catch (mgrError) {
          console.warn('Managers skipped:', mgrError.message);
        }

        renderer = CubismRenderer_WebGL.create(gl);
        renderer.setIsUsingHighPrecision(true);
        userModel.setRenderer(renderer);

        viewMatrix = new CubismMatrix44();
        viewMatrix.loadIdentity();
        viewMatrix.scale(1.0, -1.0);
        viewMatrix.translate(0.0, -0.5);
        viewMatrix.scale(1.5, 1.5);

        setIsLoaded(true);

        const loop = () => {
          if (!mounted || !modelRef.current) return;
          modelRef.current.update();
          modelRef.current.draw(renderer);

          gl.viewport(0, 0, 800, 600);
          gl.clearColor(0.0, 0.0, 0.0, 0.0);
          gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
          renderer.setMvpMatrix(viewMatrix);
          renderer.doDrawModel(modelRef.current, 0.5, 0.5);

          animationFrame.current = requestAnimationFrame(loop);
        };
        loop();

        if (phonemes.length > 0 && modelRef.current) {
          const mouthParamId = CubismId.getId('ParamMouthOpenY');
          let idx = 0;
          if (mouthTimer.current) clearInterval(mouthTimer.current);
          mouthTimer.current = setInterval(() => {
            if (!mounted || !modelRef.current || idx >= phonemes.length) {
              modelRef.current.addParameterValueById(mouthParamId, 0.0, 1.0);
              if (mouthTimer.current) clearInterval(mouthTimer.current);
              return;
            }
            const p = phonemes[idx];
            let val = 0.4;
            if (/^(aa|ae|ah|aw)$/.test(p.phoneme || '')) val = 1.0;
            else if (/^(oo|uh|er|ow)$/.test(p.phoneme || '')) val = 0.7;
            modelRef.current.addParameterValueById(mouthParamId, val, 1.0);
            idx++;
          }, 100);
        }

        if (audioUrl) {
          const audio = new Audio(audioUrl);
          audio.play().catch(err => console.warn('Audio play failed:', err));
        }

      } catch (err) {
        console.error('Live2D Init Error:', err);
        setError(err.message);
      }
    };

    initLive2D();

    return () => {
      mounted = false;
      if (animationFrame.current) cancelAnimationFrame(animationFrame.current);
      if (mouthTimer.current) clearInterval(mouthTimer.current);
      if (modelRef.current && Live2DCubismFramework) {
        modelRef.current.release();
        Live2DCubismFramework.dispose();
      }
    };
  }, [audioUrl, phonemes]);

  if (error) {
    return <div style={{ color: 'red', padding: '20px' }}>Avatar Error: {error}</div>;
  }

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={600}
      style={{
        width: '100%',
        height: '100%',
        display: 'block',
        background: 'transparent',
      }}
    />
  );
}
