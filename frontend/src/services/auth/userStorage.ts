/**
 * User storage isolation utilities for AgriSmart-AI.
 * Ensures multi-tenant isolation in localStorage so different users
 * never see each other's profile or scan history.
 */

export const ACTIVE_USER_ID_KEY = 'agrismart_active_user_id';
export const ACTIVE_SESSION_TOKEN_KEY = 'agrismart_token';

/**
 * Normalizes an email address or user identifier into a filesystem/localStorage safe key.
 */
export function normalizeIdentifier(identifier: string): string {
  return identifier.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '_');
}

/**
 * Generates or retrieves a stable, deterministic user ID for a user.
 * Prefers existing ID if provided, otherwise derives stably from normalized email.
 */
export function getStableUserId(email: string, existingId?: string): string {
  const normEmail = normalizeIdentifier(email);

  if (existingId && existingId.trim()) {
    const safeId = normalizeIdentifier(existingId);
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        localStorage.setItem(`agrismart_uid_map_${normEmail}`, safeId);
      } catch {
        // ignore storage errors
      }
    }
    return safeId;
  }

  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      const mappedId = localStorage.getItem(`agrismart_uid_map_${normEmail}`);
      if (mappedId) {
        return mappedId;
      }
      const newId = `usr_${normEmail}`;
      localStorage.setItem(`agrismart_uid_map_${normEmail}`, newId);
      return newId;
    } catch {
      // ignore storage errors
    }
  }

  return `usr_${normEmail}`;
}

/**
 * Key for storing a specific user's profile.
 */
export function getUserProfileStorageKey(userIdOrEmail: string): string {
  return `agrismart_profile_${normalizeIdentifier(userIdOrEmail)}`;
}

/**
 * Key for storing a specific user's scan history.
 */
export function getUserHistoryStorageKey(userIdOrEmail: string): string {
  return `agrismart_history_${normalizeIdentifier(userIdOrEmail)}`;
}

/**
 * Retrieves the currently active user ID from localStorage.
 */
export function getActiveUserId(): string | null {
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      return localStorage.getItem(ACTIVE_USER_ID_KEY);
    } catch {
      return null;
    }
  }
  return null;
}

/**
 * Sets the active user session.
 */
export function setActiveUserSession(userId: string, token: string): void {
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      localStorage.setItem(ACTIVE_USER_ID_KEY, userId);
      localStorage.setItem(ACTIVE_SESSION_TOKEN_KEY, token);
    } catch {
      // ignore storage errors
    }
  }
}

/**
 * Clears ONLY the active user session, leaving user profiles and histories intact.
 */
export function clearActiveUserSession(): void {
  if (typeof window !== 'undefined' && window.localStorage) {
    try {
      localStorage.removeItem(ACTIVE_USER_ID_KEY);
      localStorage.removeItem(ACTIVE_SESSION_TOKEN_KEY);
      localStorage.removeItem('agrismart_user_profile'); // legacy active key
      localStorage.removeItem('agrismart_mock_user'); // legacy mock key
    } catch {
      // ignore storage errors
    }
  }
}
