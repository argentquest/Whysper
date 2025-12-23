/**
 * main
 *
 * Application module for main.
 */
import './index.css'

import { App as AntApp } from 'antd'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route,Routes } from 'react-router-dom'

import App from './App.tsx'
import { RJSFPlayground } from './pages/RJSFPlayground'
import { ThemeProvider } from './themes'

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
            <Route path="/playground" element={<RJSFPlayground />} />
            {/* Single App with tab-based architecture */}
            <Route path="*" element={<App />} />
          </Routes>
        </AntApp>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>
)
