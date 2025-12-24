import type { UserSection } from '@/types';

const COOKIES_KEY = 'spaces_auth';
const USER_KEY = 'spaces_user';
const SECTIONS_KEY = 'spaces_sections';

export function saveCookies(cookies: string): void {
  localStorage.setItem(COOKIES_KEY, cookies);
}

export function loadCookies(): string | null {
  return localStorage.getItem(COOKIES_KEY);
}

export function clearCookies(): void {
  localStorage.removeItem(COOKIES_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(SECTIONS_KEY);
}

export function clearAllAuthData(): void {
  clearCookies();
  localStorage.removeItem('spaces_backup_cookies');
  localStorage.removeItem('spaces_backup_user');
  localStorage.removeItem('spaces_backup_sections');
}

export function migrateOldKeys(): void {
  const oldCookies = localStorage.getItem('spaces_backup_cookies');
  const oldUser = localStorage.getItem('spaces_backup_user');
  const oldSections = localStorage.getItem('spaces_backup_sections');

  if (oldCookies && !localStorage.getItem(COOKIES_KEY)) {
    localStorage.setItem(COOKIES_KEY, oldCookies);
  }
  if (oldUser && !localStorage.getItem(USER_KEY)) {
    localStorage.setItem(USER_KEY, oldUser);
  }
  if (oldSections && !localStorage.getItem(SECTIONS_KEY)) {
    localStorage.setItem(SECTIONS_KEY, oldSections);
  }

  if (oldCookies || oldUser || oldSections) {
    localStorage.removeItem('spaces_backup_cookies');
    localStorage.removeItem('spaces_backup_user');
    localStorage.removeItem('spaces_backup_sections');
  }
}

export function saveUser(user: { username: string; isCurrentUser: boolean; avatarUrl?: string }): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function loadUser(): { username: string; isCurrentUser: boolean; avatarUrl?: string } | null {
  const data = localStorage.getItem(USER_KEY);
  return data ? JSON.parse(data) : null;
}

export function saveSections(sections: UserSection[]): void {
  localStorage.setItem(SECTIONS_KEY, JSON.stringify(sections));
}

export function loadSections(): UserSection[] | null {
  const data = localStorage.getItem(SECTIONS_KEY);
  return data ? JSON.parse(data) : null;
}

