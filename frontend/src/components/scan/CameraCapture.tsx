import React, { useRef, useState, useEffect } from 'react';
import { Camera, SwitchCamera, AlertCircle, X } from 'lucide-react';
import { Button } from '../common/Button';
import { useTranslation } from '../../i18n';

interface CameraCaptureProps {
  onPhotoCaptured: (file: File) => void;
  onCancel: () => void;
  onError: (errorMessage: string) => void;
}

export const CameraCapture: React.FC<CameraCaptureProps> = ({
  onPhotoCaptured,
  onCancel,
  onError
}) => {
  const { t } = useTranslation();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');
  const [isCameraReady, setIsCameraReady] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsCameraReady(false);
  };

  const startCamera = async () => {
    stopCamera();
    setCameraError(null);

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera access is not supported on this browser or device.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: { ideal: facingMode },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setIsCameraReady(true);
      }
    } catch (err: any) {
      console.warn('Camera stream error:', err);
      const msg =
        err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError'
          ? 'Camera permission was denied. Please allow camera access in your browser settings, or use the file upload option.'
          : 'Could not access the camera. Please ensure no other app is using it, or use file upload instead.';
      setCameraError(msg);
      onError(msg);
    }
  };

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, [facingMode]);

  const toggleFacingMode = () => {
    setFacingMode((prev) => (prev === 'environment' ? 'user' : 'environment'));
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          onError('Failed to capture photo frame.');
          return;
        }
        const file = new File([blob], `leaf_camera_scan_${Date.now()}.jpg`, {
          type: 'image/jpeg'
        });
        stopCamera();
        onPhotoCaptured(file);
      },
      'image/jpeg',
      0.92
    );
  };

  return (
    <div className="relative w-full max-w-xl mx-auto rounded-3xl overflow-hidden bg-slate-950 shadow-2xl border border-slate-800">
      {/* Top Controls Overlay */}
      <div className="absolute top-4 left-4 right-4 z-20 flex items-center justify-between pointer-events-auto">
        <button
          onClick={() => {
            stopCamera();
            onCancel();
          }}
          className="p-2.5 rounded-full bg-slate-900/80 text-white hover:bg-slate-800 transition-colors"
          aria-label={t('common.close')}
        >
          <X className="w-5 h-5" />
        </button>

        <button
          onClick={toggleFacingMode}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900/80 text-white hover:bg-slate-800 text-xs font-medium transition-colors"
          aria-label="Switch camera"
        >
          <SwitchCamera className="w-4 h-4" />
          <span>{t('scan.tabCamera')}</span>
        </button>
      </div>

      {/* Video Viewport / Finder */}
      <div className="relative aspect-4/3 w-full bg-slate-900 flex items-center justify-center overflow-hidden">
        {cameraError ? (
          <div className="p-6 text-center text-rose-300 max-w-sm">
            <AlertCircle className="w-12 h-12 mx-auto mb-3 text-rose-400" />
            <p className="text-sm font-semibold mb-4">{cameraError}</p>
            <Button variant="outline" size="sm" onClick={onCancel} className="bg-white text-slate-900">
              {t('scan.tabUpload')}
            </Button>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              playsInline
              autoPlay
              muted
              className="w-full h-full object-cover"
            />
            {/* Viewfinder Target Guidelines */}
            <div className="absolute inset-8 pointer-events-none border-2 border-dashed border-emerald-400/60 rounded-2xl flex items-center justify-center">
              <div className="w-12 h-12 border-t-2 border-l-2 border-emerald-400 absolute top-0 left-0 rounded-tl-lg" />
              <div className="w-12 h-12 border-t-2 border-r-2 border-emerald-400 absolute top-0 right-0 rounded-tr-lg" />
              <div className="w-12 h-12 border-b-2 border-l-2 border-emerald-400 absolute bottom-0 left-0 rounded-bl-lg" />
              <div className="w-12 h-12 border-b-2 border-r-2 border-emerald-400 absolute bottom-0 right-0 rounded-br-lg" />
              <span className="text-xs font-semibold tracking-wider uppercase text-white/80 bg-slate-950/60 px-3 py-1 rounded-full backdrop-blur-xs">
                Center Leaf Here
              </span>
            </div>
          </>
        )}
      </div>

      {/* Hidden processing canvas */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Bottom Shutter Action Bar */}
      {!cameraError && (
        <div className="p-6 bg-slate-950 flex items-center justify-center">
          <button
            onClick={capturePhoto}
            disabled={!isCameraReady}
            className="w-20 h-20 rounded-full border-4 border-emerald-500 p-1 flex items-center justify-center active:scale-90 transition-transform disabled:opacity-50 cursor-pointer"
            aria-label="Capture leaf photo"
          >
            <div className="w-full h-full rounded-full bg-white hover:bg-emerald-100 flex items-center justify-center transition-colors">
              <Camera className="w-8 h-8 text-emerald-800" />
            </div>
          </button>
        </div>
      )}
    </div>
  );
};
