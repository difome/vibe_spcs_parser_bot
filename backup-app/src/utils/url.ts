export function extractCKFromUrl(url: string): string | null {
  if (!url) return null;
  const match = url.match(/[?&]CK=([^&]+)/);
  return match ? match[1] : null;
}

export function addCKToUrl(url: string, ck: string): string {
  if (!url || !ck) return url;
  
  if (url.includes('CK=')) {
    return url.replace(/CK=[^&]+/, `CK=${ck}`);
  }
  return url.includes('?') ? `${url}&CK=${ck}` : `${url}?CK=${ck}`;
}

