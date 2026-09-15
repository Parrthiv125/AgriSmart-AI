export type ApiErrorCode =
  | 'INVALID_IMAGE'
  | 'UNSUPPORTED_FORMAT'
  | 'FILE_TOO_LARGE'
  | 'PREDICTION_FAILED'
  | 'LOW_CONFIDENCE'
  | 'SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'UNAUTHORIZED'
  | 'NOT_FOUND';

export interface ApiError {
  code: ApiErrorCode;
  message: string;
  farmerFriendlyMessage: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  timestamp: string;
}
