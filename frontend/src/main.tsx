import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App as AntApp } from 'antd'
import { ThemeProvider } from './themes'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <AntApp>
        <App />
      </AntApp>
    </ThemeProvider>
  </StrictMode>,
)
