import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { ThemeProvider } from './themes'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AntApp>
          <Routes>
            {/* Main application */}
            <Route path="/" element={<App />} />
          </Routes>
        </AntApp>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)
