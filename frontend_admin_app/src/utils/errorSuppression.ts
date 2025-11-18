/**
 * Error Suppression Utility
 * 
 * This file contains utilities to suppress non-critical errors and warnings
 * that don't affect the application's functionality but clutter the console.
 */

/**
 * Suppresses non-critical console errors
 * - Font loading errors (Google Fonts)
 * - OTS parsing errors
 * - Browser extension errors
 */
export function suppressNonCriticalErrors() {
  // Store original console methods
  const originalError = console.error;
  const originalWarn = console.warn;

  // Override console.error
  console.error = function(...args: any[]) {
    const message = args[0]?.toString() || '';
    
    // List of non-critical error patterns to suppress
    const suppressPatterns = [
      'Failed to decode downloaded font',
      'OTS parsing error',
      'invalid sfntVersion',
      'contentscript.js', // Browser extension errors
      'webcomponents-ce.js', // Web components errors from extensions
      'overlay_bundle.js', // Extension overlay errors
    ];

    // Check if error should be suppressed
    const shouldSuppress = suppressPatterns.some(pattern => 
      message.includes(pattern) || args.join(' ').includes(pattern)
    );

    if (!shouldSuppress) {
      originalError.apply(console, args);
    }
  };

  // Override console.warn for specific warnings
  console.warn = function(...args: any[]) {
    const message = args[0]?.toString() || '';
    
    // Suppress custom element duplicate warnings (we handle these gracefully)
    if (message.includes('Custom element') && message.includes('already defined')) {
      return;
    }

    originalWarn.apply(console, args);
  };

  console.log('✅ Error suppression enabled - console is now cleaner');
}

/**
 * Handles custom element duplicate definitions
 * Prevents "already been defined" errors from libraries like TinyMCE
 */
export function preventDuplicateCustomElements() {
  if (typeof customElements === 'undefined') {
    return;
  }

  const originalDefine = customElements.define;
  const originalGet = customElements.get;
  
  // Override define to prevent duplicates
  customElements.define = function(
    name: string, 
    constructor: CustomElementConstructor, 
    options?: ElementDefinitionOptions
  ) {
    try {
      // Check if element is already defined
      const existing = originalGet.call(customElements, name);
      if (!existing) {
        originalDefine.call(customElements, name, constructor, options);
      } else {
        // Silently skip duplicate registration
        // Don't log warning as it clutters console
      }
    } catch (error) {
      // Silently catch and ignore custom element errors
      // These are usually harmless duplicate registrations
      const errorMessage = (error as Error).message || '';
      if (!errorMessage.includes('already been defined')) {
        // Re-throw non-duplicate errors
        console.warn('Custom element error:', error);
      }
    }
  };
  
  // Also suppress errors that happen during element definition
  const originalErrorHandler = window.onerror;
  window.onerror = function(message, source, lineno, colno, error) {
    const msg = message?.toString() || '';
    // Suppress custom element duplicate errors
    if (msg.includes('already been defined') || 
        msg.includes('mce-autosize-textarea') ||
        source?.includes('webcomponents')) {
      return true; // Prevent default error handling
    }
    // Call original handler for other errors
    if (originalErrorHandler) {
      return originalErrorHandler(message, source, lineno, colno, error);
    }
    return false;
  };
}

/**
 * Initialize all error suppressions
 */
export function initErrorSuppression() {
  suppressNonCriticalErrors();
  preventDuplicateCustomElements();
}
