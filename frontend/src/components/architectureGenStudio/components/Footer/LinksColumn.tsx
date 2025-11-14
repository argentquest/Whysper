/**
 * Links Column Component
 * Displays about/help links and disclaimer
 */

import React from 'react';
import { Space, Typography, Divider, theme } from 'antd';

type LinksColumnVariant = 'compact' | 'legal';

const compactLinks = [
  { label: 'Help', url: 'https://www.wellsfargo.com/help/' },
  { label: 'About Wells Fargo', url: 'https://www.wellsfargo.com/about/' },
  { label: 'Contact Us', url: 'https://www.wellsfargo.com/help/contact-us/' },
];

const legalLinks = [
  { label: 'Privacy, Cookies, and Legal', url: 'https://www.wellsfargo.com/privacy-security/' },
  { label: 'Online Access Agreement', url: 'https://www.wellsfargo.com/online-banking/online-access-agreement/' },
  { label: 'Ad Choices', url: 'https://www.wellsfargo.com/privacy-security/online/privacy/#advertising' },
  { label: 'Give Feedback', url: 'https://www.wellsfargo.com/appointments/' },
];

interface LinksColumnProps {
  variant?: LinksColumnVariant;
  align?: 'left' | 'right' | 'center';
}

export const LinksColumn: React.FC<LinksColumnProps> = ({
  variant = 'legal',
  align = 'right',
}) => {
  const items = variant === 'compact' ? compactLinks : legalLinks;
  const { token } = theme.useToken();
  const linkColor = (token as Record<string, string>).colorBrandLink ?? token.colorLink ?? '#004c97';

  if (variant === 'compact') {
    return (
      <Space
        size={8}
        style={{
          width: '100%',
          justifyContent: align === 'left' ? 'flex-start' : align === 'center' ? 'center' : 'flex-end',
        }}
      >
        {items.map((item, index) => (
          <React.Fragment key={item.label}>
            {index > 0 && <Divider type="vertical" style={{ height: '16px', margin: 0, borderColor: '#e3ded8' }} />}
            <Typography.Link
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: linkColor, fontWeight: 600, fontSize: 13 }}
            >
              {item.label}
            </Typography.Link>
          </React.Fragment>
        ))}
      </Space>
    );
  }

  return (
    <Space
      size={[16, 8]}
      wrap
      style={{
        width: '100%',
        justifyContent: align === 'left' ? 'flex-start' : align === 'center' ? 'center' : 'flex-end',
      }}
    >
      {items.map((item) => (
        <Typography.Link
          key={item.label}
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: linkColor,
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          {item.label}
        </Typography.Link>
      ))}
    </Space>
  );
};

export default LinksColumn;
