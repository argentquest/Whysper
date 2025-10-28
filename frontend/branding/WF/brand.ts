/**
 * Wells Fargo Brand Configuration
 *
 * Contains brand metadata, messaging, and identity elements
 */

export const WFBrand = {
  // Brand Identity
  name: 'Wells Fargo AI Archtect Helper',
  fullName: 'Wells Fargo AI Architect Assistant',
  tagline: 'AI Code Assistant',
  version: '2.0.0',

  // Brand Messaging
  description: 'AI-Powered Code Analysis & Development Assistant',

  // Logo Configuration
  logo: {
    type: 'emoji' as const, // or 'image' | 'svg'
    emoji: '🧠',
    backgroundColor: '#b31e30', // Deep Red
    alt: 'Whysper Logo',
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
