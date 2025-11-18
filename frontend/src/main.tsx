/**
 * main
 * 
 * Application module for main.
 */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { ThemeProvider } from './themes'
import './index.css'
import App from './App.tsx'

// Create React root and render the entire application with multiple layers of providers
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* Wrap app in strict mode for additional runtime checks and warnings */}
    <BrowserRouter>
      {/* Enable client-side routing for single page application navigation */}
      <ThemeProvider>
        {/* Apply global theme configuration across the entire app */}
        <AntApp>
          {/* Ant Design app wrapper for consistent styling and components */}
          <Routes>
            {/* Single App with tab-based architecture */}
            <Route path="*" element={<App />} />
          </Routes>
        </AntApp>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)