/**
 * Footer Component - Status Bar
 * Displays status, SSE messages, and links
 */

import React from 'react';
import { Layout, Row, Col, Divider, Typography, Space, theme } from 'antd';
import type { FooterProps } from '../../types';
import { StatusColumn } from './StatusColumn';
import { SSEMessagesColumn } from './SSEMessagesColumn';
import { LinksColumn } from './LinksColumn';

const footerLinks = [
  {
    title: 'Customer Service',
    links: [
      { label: 'Sign On', url: 'https://www.wellsfargo.com/' },
      { label: 'Customer Service', url: 'https://www.wellsfargo.com/help/' },
      { label: 'Security Center', url: 'https://www.wellsfargo.com/privacy-security/' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Routing Numbers', url: 'https://www.wellsfargo.com/help/routing-number/' },
      { label: 'International Services', url: 'https://www.wellsfargo.com/com/international/' },
      { label: 'Report Fraud', url: 'https://www.wellsfargo.com/privacy-security/fraud/report/' },
    ],
  },
  {
    title: 'Business Solutions',
    links: [
      { label: 'Commercial banking', url: 'https://www.wellsfargo.com/com/' },
      { label: 'Corporate & Investment', url: 'https://www.wellsfargo.com/com/corporate-investment-banking/' },
      { label: 'Insights & reports', url: 'https://www.wellsfargo.com/com/insights/' },
    ],
  },
];

const disclaimerLines = [
  'Not Insured by the FDIC or Any Federal Government Agency',
  'Not a Deposit or Other Obligation of, or Guaranteed by, the Bank or Any Bank Affiliate',
  'Subject to Investment Risks, Including Possible Loss of the Principal Amount Invested',
];

export const Footer: React.FC<FooterProps> = ({
  currentStatus,
  sseMessages,
  unreadMessageCount,
  isSSEConnected = false,
}) => {
  const { token } = theme.useToken();
  const footerBg = (token as Record<string, string>).colorBrandFooterBg ?? token.colorBgLayout ?? '#f8f4f1';
  const footerBorder = (token as Record<string, string>).colorBrandFooterBorder ?? token.colorBorder ?? '#f7b500';
  const footerCard = (token as Record<string, string>).colorBrandFooterCardBg ?? token.colorBgContainer ?? '#ffffff';
  const footerText = (token as Record<string, string>).colorBrandFooterText ?? token.colorText ?? '#231f20';
  const footerMuted = (token as Record<string, string>).colorBrandMutedText ?? token.colorTextSecondary ?? '#5d5550';
  const linkColor = (token as Record<string, string>).colorBrandLink ?? token.colorLink ?? '#004c97';
  const strokeColor = (token as Record<string, string>).colorBrandFooterBorder ?? token.colorBorder ?? '#e3ded8';

  return (
    <Layout.Footer
      style={{
        padding: '32px clamp(16px, 4vw, 64px) 16px',
        borderTop: `4px solid ${footerBorder}`,
        backgroundColor: 'transparent',
        color: footerText,
      }}
    >
      <div
        style={{
          backgroundColor: footerCard,
          border: `1px solid ${strokeColor}`,
          borderRadius: 16,
          padding: '20px clamp(16px, 3vw, 32px)',
          marginBottom: 32,
        }}
      >
        <Row gutter={[24, 16]} align="middle">
          <Col xs={24} md={8}>
            <Typography.Text style={{ display: 'block', marginBottom: 6, fontWeight: 600, color: footerMuted }}>
              Current status
            </Typography.Text>
            <StatusColumn status={currentStatus} />
          </Col>
          <Col xs={24} md={8}>
            <Typography.Text style={{ display: 'block', marginBottom: 6, fontWeight: 600, color: footerMuted }}>
              Processing updates
            </Typography.Text>
            <SSEMessagesColumn
              messages={sseMessages}
              isConnected={isSSEConnected}
              unreadCount={unreadMessageCount}
            />
          </Col>
          <Col xs={24} md={8} style={{ textAlign: 'right' }}>
            <Typography.Text style={{ display: 'block', marginBottom: 6, fontWeight: 600, color: footerMuted }}>
              Quick assistance
            </Typography.Text>
            <LinksColumn variant="compact" align="right" />
          </Col>
        </Row>
      </div>

      <Row gutter={[32, 24]} style={{ width: '100%' }}>
        {footerLinks.map((section) => (
          <Col xs={24} md={8} key={section.title}>
            <Typography.Title level={5} style={{ marginBottom: 12, color: footerText }}>
              {section.title}
            </Typography.Title>
            <Space direction="vertical" size={4}>
              {section.links.map((link) => (
                <Typography.Link
                  key={link.label}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: linkColor,
                    fontSize: 13,
                    fontWeight: 600,
                  }}
                >
                  {link.label}
                </Typography.Link>
              ))}
            </Space>
          </Col>
        ))}
      </Row>

      <Divider style={{ borderColor: strokeColor, margin: '28px 0 16px' }} />

      <Row gutter={[24, 16]} align="middle" style={{ width: '100%' }}>
        <Col xs={24} lg={14}>
          <div style={{ fontSize: 13, color: footerMuted }}>
            <Typography.Text strong style={{ color: footerText }}>
              Investment and Insurance Products:
            </Typography.Text>
            <ul style={{ margin: '8px 0 0 16px', padding: 0, listStyle: 'disc', color: footerMuted }}>
              {disclaimerLines.map((line) => (
                <li key={line} style={{ marginBottom: 2 }}>{line}</li>
              ))}
            </ul>
          </div>
        </Col>
        <Col xs={24} lg={10} style={{ textAlign: 'right' }}>
          <LinksColumn variant="legal" align="right" />
        </Col>
      </Row>

      <Typography.Text style={{ display: 'block', textAlign: 'right', fontSize: 12, marginTop: 12, color: footerMuted }}>
        © {new Date().getFullYear()} Wells Fargo. All rights reserved.
      </Typography.Text>
    </Layout.Footer>
  );
};

export default Footer;
