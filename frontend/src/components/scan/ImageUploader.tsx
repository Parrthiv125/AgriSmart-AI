import React, { useRef, useState, DragEvent, ChangeEvent } from 'react';
import { UploadCloud, Image as ImageIcon, ShieldCheck } from 'lucide-react';
import { Button } from '../common/Button';
import { useTranslation } from '../../i18n';

interface ImageUploaderProps {
  onImageSelected: (file: File) => void;
  onError: (errorMessage: string) => void;
}

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageSelected, onError }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const { t } = useTranslation();

  const validateAndProcessFile = (file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type.toLowerCase())) {
      onError('Unsupported image format. Please upload a JPG, PNG, or WebP photo of the crop leaf.');
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      onError(`File is too large (${(file.size / (1024 * 1024)).toFixed(1)}MB). Please choose an image smaller than ${MAX_SIZE_MB}MB.`);
      return;
    }

    onImageSelected(file);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        accept=".jpg,.jpeg,.png,.webp"
        className="hidden"
        id="leaf-file-input"
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-3xl border-2 border-dashed p-8 sm:p-12 transition-all flex flex-col items-center justify-center text-center group ${
          isDragging
            ? 'border-emerald-500 bg-emerald-50/80 scale-[1.01]'
            : 'border-slate-300 hover:border-emerald-400 bg-white/80 hover:bg-emerald-50/20 shadow-xs'
        }`}
      >
        <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform shadow-xs">
          <UploadCloud className="w-8 h-8 sm:w-10 sm:h-10" />
        </div>

        <h3 className="text-lg sm:text-xl font-bold text-slate-900 mb-1">
          {t('scan.dragDropText')}
        </h3>
        <p className="text-sm text-slate-500 max-w-sm mb-4">
          {t('scan.orBrowseText')} ({t('scan.fileLimitHint')})
        </p>

        <Button
          type="button"
          variant="secondary"
          size="md"
          icon={<ImageIcon className="w-4 h-4" />}
          onClick={(e) => {
            e.stopPropagation();
            fileInputRef.current?.click();
          }}
        >
          {t('scan.browseFilesBtn')}
        </Button>
      </div>

      {/* Helpful leaf capture tip */}
      <div className="mt-4 p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200/60 flex items-start gap-3 text-xs sm:text-sm text-emerald-900">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
        <p>
          <strong className="font-semibold text-emerald-950">{t('scan.notice')}: </strong>
          {t('scan.cameraInstructions')}
        </p>
      </div>
    </div>
  );
};
