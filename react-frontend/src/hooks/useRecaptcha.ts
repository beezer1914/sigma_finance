import { useCallback, useEffect, useState } from 'react';

declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      execute: (siteKey: string, options: { action: string }) => Promise<string>;
    };
  }
}

const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY || '';

export function useRecaptcha() {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Don't load if no site key configured
    if (!RECAPTCHA_SITE_KEY) {
      console.warn('reCAPTCHA site key not configured');
      return;
    }

    // Check if script already exists
    if (document.querySelector(`script[src*="recaptcha"]`)) {
      setIsLoaded(true);
      return;
    }

    // Load reCAPTCHA v3 script
    const script = document.createElement('script');
    script.src = `https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`;
    script.async = true;
    script.onload = () => {
      window.grecaptcha.ready(() => {
        setIsLoaded(true);
      });
    };
    document.head.appendChild(script);

    return () => {
      // Cleanup not needed for reCAPTCHA script
    };
  }, []);

  const executeRecaptcha = useCallback(async (action: string): Promise<string | null> => {
    if (!RECAPTCHA_SITE_KEY) {
      console.warn('reCAPTCHA not configured, skipping verification');
      return null;
    }

    if (!isLoaded || !window.grecaptcha) {
      console.warn('reCAPTCHA not loaded yet');
      return null;
    }

    try {
      const token = await window.grecaptcha.execute(RECAPTCHA_SITE_KEY, { action });
      return token;
    } catch (error) {
      console.error('reCAPTCHA execution failed:', error);
      return null;
    }
  }, [isLoaded]);

  return { executeRecaptcha, isLoaded, isConfigured: !!RECAPTCHA_SITE_KEY };
}
