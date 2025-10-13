import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { ThemeProvider } from './themes'
import './index.css'
import App from './App.tsx'
import { DiagramRenderer } from './pages/DiagramRenderer'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AntApp>
          <Routes>
            {/* Main application */}
            <Route path="/" element={<App />} />

            {/* Headless diagram renderer for Playwright */}
            <Route path="/render" element={<DiagramRenderer />} />
          </Routes>
        </AntApp>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)
