import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { App as AntApp } from 'antd'
import { ThemeProvider } from './themes'
import './index.css'
import App from './App.tsx'
import StudioUI from './components/architectureGenStudio'
import DiagramWizardPage from './pages/DiagramWizardPage'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AntApp>
          <Routes>
            {/* Main application */}
            <Route path="/" element={<App />} />
            {/* Architecture Gen Studio - Diagram Generation Tool */}
            <Route path="/studio" element={<StudioUI />} />
            {/* AI Diagram Wizard - LangGraph-powered diagram generation */}
            <Route path="/diagram-wizard" element={<DiagramWizardPage />} />
          </Routes>
        </AntApp>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
)
