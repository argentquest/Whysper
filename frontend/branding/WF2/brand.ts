/**
 * Wells Fargo Brand Configuration
 *
 * Contains brand metadata, messaging, and identity elements
 */

import wfLogo from './assets/wf-logo.png';

export const WFBrand = {
  // Brand Identity
  name: 'Wells Fargo AI Architect Helper',
  fullName: 'Wells Fargo AI Architect Assistant',
  tagline: 'AI Code Assistant',
  version: '2.0.0',

  // Brand Messaging
  description: 'AI-Powered Code Analysis & Development Assistant',

  // Logo Configuration
  logo: {
    type: 'image' as const,
    src: wfLogo,
    backgroundColor: '#b31e30',
    alt: 'Wells Fargo Logo',
  },

  // Brand Voice
  voice: {
    tone: 'professional, trustworthy, innovative',
    attributes: ['reliable', 'intelligent', 'efficient', 'secure'],
  },

  // Social/Contact (if applicable)
  links: {
    website: '',
    documentation: '',
    support: '',
    github: '',
  },

  // Feature Set
  features: [
    'Natural language code interaction',
    'Multi-agent AI system',
    'Context-aware assistance',
    'File editing capabilities',
    'Documentation generation',
    'Code analysis',
    'Real-time collaboration',
  ],

  // Technology Stack
  techStack: {
    frontend: ['React', 'TypeScript', 'Vite', 'Ant Design'],
    backend: ['Python', 'FastAPI'],
    ai: ['OpenAI', 'Anthropic Claude', 'Custom Agents'],
  },
} as const;

export type WFBrandConfig = typeof WFBrand;
