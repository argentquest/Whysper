/// <reference types="vite/client" /> // Reference Vite's client type definitions for environment support

// Define an interface for environment variables with type safety
// Allows accessing environment variables with readonly protection
interface ImportMetaEnv {
  readonly VITE_API_URL?: string // Optional API URL from .env file
  readonly VITE_BACKEND_PROTOCOL?: string // Optional protocol override for backend (http/https)
  // Add other environment variables here as needed
}

// Define ImportMeta interface to provide type-safe access to environment variables
// Ensures type checking and intellisense for environment configurations
interface ImportMeta {
  readonly env: ImportMetaEnv // Readonly access to environment variables
}

// Declare module for .woff font files to enable importing font files
// Allows TypeScript to recognize and type these file imports correctly
declare module '*.woff' {
  const src: string // Exports font file path as a string
  export default src
}

// Similar declaration for .woff2 font files
// Provides type support for different font file formats
declare module '*.woff2' {
  const src: string // Exports font file path as a string
  export default src
}
