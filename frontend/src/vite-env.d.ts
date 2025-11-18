/**
 * vite-env.d
 * 
 * Application module for vite-env.d.
 */
/// <reference types="vite/client" />

/**
 * ImportMetaEnv type definition
 * 
 * Describes the structure and properties of ImportMetaEnv
 */
interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  // Add other environment variables here as needed
}

/**
 * ImportMeta type definition
 * 
 * Describes the structure and properties of ImportMeta
 */
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module '*.woff' {
  const src: string;
  export default src;
}

declare module '*.woff2' {
  const src: string;
  export default src;
}
