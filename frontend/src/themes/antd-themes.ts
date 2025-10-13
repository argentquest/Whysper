import { theme } from 'antd';

// Base theme configuration
const baseTheme = {
  token: {
    borderRadius: 6,
    wireframe: false,
  },
  components: {
    Button: {
      borderRadius: 6,
    },
    Input: {
      borderRadius: 6,
    },
    Card: {
      borderRadius: 8,
    },
  },
};

// Theme definitions with Pro-inspired designs
export const themes = {
  // Default Ant Design themes
  light: {
    name: 'Light',
    algorithm: theme.defaultAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#1890ff',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#1890ff',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#ffffff',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#e6f7ff',
        itemHoverBg: '#f5f5f5',
      },
    },
  },

  dark: {
    name: 'Dark',
    algorithm: theme.darkAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#1890ff',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#1890ff',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#141414',
        siderBg: '#1f1f1f',
        headerBg: '#1f1f1f',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#111b26',
        itemHoverBg: '#262626',
      },
    },
  },

  // Pro-inspired themes
  proBlue: {
    name: 'Pro Blue',
    algorithm: theme.defaultAlgorithm,
    token: {
      borderRadius: 12,
      wireframe: false,
      colorPrimary: '#667eea',
      colorSuccess: '#10b981',
      colorWarning: '#f59e0b',
      colorError: '#ef4444',
      colorInfo: '#667eea',
      colorBgContainer: '#ffffff',
      colorBgElevated: '#ffffff',
      colorBgLayout: '#fafbfc',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif',
      fontSize: 14,
      lineHeight: 1.6,
      boxShadow: '0 4px 12px 0 rgba(0, 0, 0, 0.05)',
      boxShadowSecondary: '0 2px 8px 0 rgba(0, 0, 0, 0.06)',
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
    },
    components: {
      Layout: {
        bodyBg: '#fafbfc',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
        headerHeight: 64,
        headerPadding: '0 24px',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#f0f4ff',
        itemHoverBg: '#f8fafc',
        itemBorderRadius: 8,
      },
      Button: {
        borderRadius: 8,
        controlHeight: 40,
        controlHeightLG: 48,
        controlHeightSM: 32,
        paddingContentHorizontal: 16,
        fontWeight: 500,
      },
      Card: {
        borderRadius: 16,
        paddingLG: 24,
        headerBg: 'transparent',
        bodyPadding: 20,
      },
      Input: {
        borderRadius: 12,
        controlHeight: 44,
        paddingBlock: 12,
        paddingInline: 16,
        fontSize: 15,
        lineHeight: 1.6,
      },
      Select: {
        borderRadius: 8,
        controlHeight: 40,
        optionPadding: '8px 12px',
      },
      Modal: {
        borderRadius: 16,
        headerBg: 'transparent',
        contentBg: '#ffffff',
      },
      Tabs: {
        borderRadius: 8,
        cardBg: '#ffffff',
        itemColor: '#64748b',
        itemSelectedColor: '#667eea',
        itemHoverColor: '#667eea',
      },
    },
  },

  proDark: {
    name: 'Pro Dark',
    algorithm: theme.darkAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#1677ff',
      colorSuccess: '#00b96b',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#1677ff',
      colorBgContainer: '#1f1f1f',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#000000',
        siderBg: '#141414',
        headerBg: '#141414',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#111b26',
        itemHoverBg: '#262626',
      },
    },
  },

  // Modern color schemes
  purple: {
    name: 'Purple',
    algorithm: theme.defaultAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#722ed1',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#722ed1',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#f9f0ff',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#f9f0ff',
        itemHoverBg: '#f5f5f5',
      },
    },
  },

  green: {
    name: 'Green',
    algorithm: theme.defaultAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#52c41a',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#52c41a',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#f6ffed',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#f6ffed',
        itemHoverBg: '#f5f5f5',
      },
    },
  },

  orange: {
    name: 'Orange',
    algorithm: theme.defaultAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#fa8c16',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#fa8c16',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#fff7e6',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#fff7e6',
        itemHoverBg: '#f5f5f5',
      },
    },
  },

  red: {
    name: 'Red',
    algorithm: theme.defaultAlgorithm,
    token: {
      ...baseTheme.token,
      colorPrimary: '#f5222d',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#f5222d',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#fff2f0',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#fff2f0',
        itemHoverBg: '#f5f5f5',
      },
    },
  },

  // Compact theme
  compact: {
    name: 'Compact',
    algorithm: [theme.defaultAlgorithm, theme.compactAlgorithm],
    token: {
      ...baseTheme.token,
      colorPrimary: '#1890ff',
      colorSuccess: '#52c41a',
      colorWarning: '#faad14',
      colorError: '#ff4d4f',
      colorInfo: '#1890ff',
    },
    components: {
      ...baseTheme.components,
      Layout: {
        bodyBg: '#ffffff',
        siderBg: '#ffffff',
        headerBg: '#ffffff',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: '#e6f7ff',
        itemHoverBg: '#f5f5f5',
      },
    },
  },

  // Modern gradient theme with beautiful backgrounds
  modernGradient: {
    name: 'Modern Gradient',
    algorithm: theme.defaultAlgorithm,
    token: {
      borderRadius: 16,
      wireframe: false,
      colorPrimary: '#6366f1',
      colorSuccess: '#10b981',
      colorWarning: '#f59e0b',
      colorError: '#ef4444',
      colorInfo: '#6366f1',
      colorBgContainer: '#ffffff',
      colorBgElevated: '#ffffff',
      colorBgLayout: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif',
      fontSize: 14,
      lineHeight: 1.6,
      boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      boxShadowSecondary: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      controlHeight: 44,
      controlHeightLG: 52,
      controlHeightSM: 36,
    },
    components: {
      Layout: {
        bodyBg: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        siderBg: 'rgba(255, 255, 255, 0.95)',
        headerBg: 'rgba(255, 255, 255, 0.95)',
        headerHeight: 64,
        headerPadding: '0 24px',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: 'rgba(99, 102, 241, 0.1)',
        itemHoverBg: 'rgba(99, 102, 241, 0.05)',
        itemBorderRadius: 12,
      },
      Button: {
        borderRadius: 12,
        controlHeight: 44,
        controlHeightLG: 52,
        controlHeightSM: 36,
        paddingContentHorizontal: 20,
        fontWeight: 500,
        defaultBg: 'rgba(255, 255, 255, 0.9)',
        defaultBorderColor: 'rgba(229, 231, 235, 0.8)',
      },
      Card: {
        borderRadius: 20,
        paddingLG: 24,
        headerBg: 'transparent',
        bodyPadding: 24,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      },
      Input: {
        borderRadius: 14,
        controlHeight: 48,
        paddingBlock: 14,
        paddingInline: 18,
        fontSize: 15,
        lineHeight: 1.6,
      },
      Select: {
        borderRadius: 12,
        controlHeight: 44,
        optionPadding: '12px 16px',
      },
      Modal: {
        borderRadius: 20,
        headerBg: 'transparent',
        contentBg: 'rgba(255, 255, 255, 0.98)',
      },
      Tabs: {
        borderRadius: 12,
        cardBg: 'rgba(255, 255, 255, 0.95)',
        itemColor: '#64748b',
        itemSelectedColor: '#6366f1',
        itemHoverColor: '#6366f1',
        inkBarColor: '#6366f1',
      },
    },
  },

  // Dark version of the modern gradient theme
  modernGradientDark: {
    name: 'Modern Gradient Dark',
    algorithm: theme.darkAlgorithm,
    token: {
      borderRadius: 16,
      wireframe: false,
      colorPrimary: '#818cf8',
      colorSuccess: '#34d399',
      colorWarning: '#fbbf24',
      colorError: '#f87171',
      colorInfo: '#818cf8',
      colorBgContainer: 'rgba(30, 41, 59, 0.95)',
      colorBgElevated: 'rgba(30, 41, 59, 0.98)',
      colorBgLayout: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif',
      fontSize: 14,
      lineHeight: 1.6,
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
      boxShadowSecondary: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
      controlHeight: 44,
      controlHeightLG: 52,
      controlHeightSM: 36,
    },
    components: {
      Layout: {
        bodyBg: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        siderBg: 'rgba(30, 41, 59, 0.95)',
        headerBg: 'rgba(30, 41, 59, 0.95)',
        headerHeight: 64,
        headerPadding: '0 24px',
      },
      Menu: {
        itemBg: 'transparent',
        itemSelectedBg: 'rgba(129, 140, 248, 0.2)',
        itemHoverBg: 'rgba(129, 140, 248, 0.1)',
        itemBorderRadius: 12,
      },
      Button: {
        borderRadius: 12,
        controlHeight: 44,
        controlHeightLG: 52,
        controlHeightSM: 36,
        paddingContentHorizontal: 20,
        fontWeight: 500,
      },
      Card: {
        borderRadius: 20,
        paddingLG: 24,
        headerBg: 'transparent',
        bodyPadding: 24,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3)',
      },
      Input: {
        borderRadius: 14,
        controlHeight: 48,
        paddingBlock: 14,
        paddingInline: 18,
        fontSize: 15,
        lineHeight: 1.6,
      },
      Select: {
        borderRadius: 12,
        controlHeight: 44,
        optionPadding: '12px 16px',
      },
      Modal: {
        borderRadius: 20,
        headerBg: 'transparent',
        contentBg: 'rgba(30, 41, 59, 0.98)',
      },
      Tabs: {
        borderRadius: 12,
        cardBg: 'rgba(30, 41, 59, 0.95)',
        itemColor: '#94a3b8',
        itemSelectedColor: '#818cf8',
        itemHoverColor: '#818cf8',
        inkBarColor: '#818cf8',
      },
    },
  },
};

export type ThemeKey = keyof typeof themes;
export type ThemeMode = ThemeKey; // Updated to support all theme keys

export const getThemeConfig = (themeKey: ThemeKey) => {
  const selectedTheme = themes[themeKey];
  return {
    algorithm: selectedTheme.algorithm,
    token: selectedTheme.token,
    components: selectedTheme.components,
  };
};

export const getThemeList = () => {
  return Object.entries(themes).map(([key, theme]) => ({
    key: key as ThemeKey,
    name: theme.name,
    primary: theme.token.colorPrimary,
  }));
};