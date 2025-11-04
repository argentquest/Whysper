# Architecture Gen Studio - Deployment Guide

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Theme Testing](#theme-testing)
3. [Performance Optimization](#performance-optimization)
4. [Cross-Browser Testing](#cross-browser-testing)
5. [Deployment Steps](#deployment-steps)
6. [Post-Deployment Verification](#post-deployment-verification)

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All TypeScript errors resolved (0 errors)
- [ ] All ESLint warnings addressed
- [ ] No console errors or warnings in production build
- [ ] Code follows project style guide
- [ ] All components properly typed (no `any` types)

### Testing
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing completed
- [ ] Error scenarios tested
- [ ] All workflows validated

### Accessibility
- [ ] WCAG 2.1 AA compliance verified
- [ ] Keyboard navigation tested
- [ ] Screen reader testing completed (3 tools)
- [ ] Color contrast verified
- [ ] Focus management working

### Performance
- [ ] Page load time < 3s
- [ ] API responses < 5s
- [ ] Diagram rendering < 10s
- [ ] Bundle size optimized
- [ ] No memory leaks detected

### Documentation
- [ ] README updated
- [ ] API documentation complete
- [ ] User guide written
- [ ] Deployment procedures documented
- [ ] Troubleshooting guide created

---

## Theme Testing

### Supported Themes
The application supports multiple Ant Design themes via Whysper's ThemeProvider:

1. **Default (Light)**
   - Primary color: Ant Design Blue (#1890ff)
   - Background: White
   - Text: Dark gray

2. **Dark**
   - Primary color: Ant Design Blue (#1890ff)
   - Background: Dark gray
   - Text: White

3. **Custom Themes** (via Whysper configuration)
   - Can be extended with additional color schemes
   - All colors must meet WCAG AA contrast requirements

### Theme Testing Checklist

#### Color Verification
- [ ] Primary buttons visible in all themes
- [ ] Error messages visible in all themes
- [ ] Success messages visible in all themes
- [ ] Text readable on backgrounds
- [ ] Borders visible in all themes

#### Component Styling
- [ ] Columns render correctly
- [ ] Headers properly styled
- [ ] Footers properly styled
- [ ] Modals styled correctly
- [ ] Buttons styled correctly
- [ ] Input fields visible

#### Dark Mode Specific
- [ ] SVG diagrams readable on dark background
- [ ] Code editor readable
- [ ] Text has sufficient contrast
- [ ] Icons visible

### Theme Testing Process

```bash
# 1. Build with different theme
npm run build

# 2. Test in browser
open http://localhost:3000/studio

# 3. Switch themes via Whysper settings (if available)

# 4. Verify all UI elements visible and readable

# 5. Capture screenshots for documentation
```

### Theme Color Checklist

```typescript
// Critical colors that must be verified in each theme
const criticalColors = [
  '--ant-color-primary',      // Buttons, links
  '--ant-color-error',        // Error messages
  '--ant-color-success',      // Success messages
  '--ant-color-warning',      // Warning messages
  '--ant-color-text',         // Primary text
  '--ant-color-text-secondary', // Secondary text
  '--ant-color-bg-container', // Container backgrounds
  '--ant-color-border',       // Borders
];

// Each color must have >= 4.5:1 contrast on intended background
```

---

## Performance Optimization

### Bundle Size
- [ ] Main bundle < 200KB gzipped
- [ ] Component library properly tree-shaken
- [ ] Unused dependencies removed
- [ ] Minification enabled

### Runtime Performance
- [ ] No unnecessary re-renders
- [ ] Memoization used appropriately
- [ ] useCallback for event handlers
- [ ] useMemo for expensive computations

### API Performance
- [ ] Request batching implemented
- [ ] Caching strategy in place
- [ ] SSE reconnection optimized
- [ ] Timeouts reasonable

### Local Storage
- [ ] No large objects stored
- [ ] Cleanup on logout
- [ ] Quota exceeded handled
- [ ] Old data removed periodically

### Code Splitting
```typescript
// Lazy load diagram components if needed
const ArchitectureGenStudio = lazy(
  () => import('./components/architectureGenStudio')
);

// Suspense boundary
<Suspense fallback={<Spinner />}>
  <ArchitectureGenStudio />
</Suspense>
```

### Performance Monitoring

```typescript
// Add Web Vitals monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

### Optimization Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| First Contentful Paint (FCP) | < 1.8s | TBD | ⏳ |
| Largest Contentful Paint (LCP) | < 2.5s | TBD | ⏳ |
| Cumulative Layout Shift (CLS) | < 0.1 | TBD | ⏳ |
| First Input Delay (FID) | < 100ms | TBD | ⏳ |
| Time to First Byte (TTFB) | < 600ms | TBD | ⏳ |

---

## Cross-Browser Testing

### Supported Browsers

#### Desktop
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)

#### Mobile
- [ ] iOS Safari (latest 2 versions)
- [ ] Chrome Android (latest 2 versions)
- [ ] Firefox Android (latest 2 versions)

#### Minimum Requirements
- ES2015+ support required
- CSS Grid support required
- Fetch API support required
- localStorage support required

### Browser Testing Checklist

#### Layout
- [ ] Three-column layout renders correctly
- [ ] Columns resize smoothly
- [ ] Collapse/expand buttons work
- [ ] Responsive breakpoints work
- [ ] No horizontal scrolling

#### Interactions
- [ ] Dropdowns open and close
- [ ] Modals appear and close
- [ ] Form inputs work
- [ ] Buttons clickable
- [ ] Zoom controls responsive

#### Rendering
- [ ] SVG diagrams render correctly
- [ ] Code syntax highlighting works
- [ ] Loading spinners animate
- [ ] Transitions smooth
- [ ] No flickering

#### APIs
- [ ] Fetch requests work
- [ ] SSE connections work
- [ ] localStorage works
- [ ] Timers work
- [ ] Event listeners work

### Browser-Specific Issues

#### Chrome/Edge
- [ ] Smooth scrolling works
- [ ] Hardware acceleration working
- [ ] DevTools integration

#### Firefox
- [ ] SVG rendering
- [ ] CSS Grid layout
- [ ] Flexbox layout

#### Safari/iOS
- [ ] Sticky positioning (if used)
- [ ] Scroll behavior
- [ ] Touch interactions
- [ ] Mobile viewport
- [ ] Safe area insets

### Testing Tools
- [BrowserStack](https://www.browserstack.com/)
- [LambdaTest](https://www.lambdatest.com/)
- [Sauce Labs](https://saucelabs.com/)
- Manual testing on physical devices

---

## Deployment Steps

### 1. Pre-Deployment Build

```bash
# Install dependencies
npm install

# Run tests
npm run test

# Build for production
npm run build

# Verify build output
ls -la dist/
```

### 2. Build Verification

```bash
# Check bundle size
npm run build -- --report

# Analyze dependencies
npm ls

# Check for vulnerabilities
npm audit
```

### 3. Staging Deployment

```bash
# Deploy to staging environment
npm run deploy:staging

# Run smoke tests
npm run test:smoke:staging

# Verify all endpoints
curl https://staging.example.com/api/v1/health
```

### 4. Production Deployment

```bash
# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Deploy to production
npm run deploy:prod

# Verify deployment
curl https://example.com/api/v1/health
```

### 5. Rollback Plan

```bash
# If deployment fails, rollback to previous version
npm run deploy:rollback

# Verify rollback successful
curl https://example.com/api/v1/health
```

---

## Post-Deployment Verification

### Immediate Checks (First Hour)

```bash
# 1. Check application loads
curl https://example.com/studio

# 2. Check API endpoints
curl https://example.com/api/v1/agents
curl https://example.com/api/v1/agents/agent-1/options

# 3. Check SSL certificate
openssl s_client -connect example.com:443

# 4. Check monitoring
# - Error rates low
# - Response times normal
# - No unusual API usage
```

### Functional Verification

- [ ] Home page loads within 3 seconds
- [ ] Agent dropdown shows agents
- [ ] Can select agent and view options
- [ ] Can edit and submit prompt
- [ ] Can view generated diagram
- [ ] Can edit code and validate
- [ ] Can render custom code
- [ ] Can export diagram
- [ ] Can switch diagram types
- [ ] Footer status shows updates
- [ ] SSE messages appear
- [ ] Logout works

### Performance Verification

```bash
# Run Lighthouse audit
lighthouse https://example.com/studio --view

# Check Core Web Vitals
# - LCP < 2.5s
# - FID < 100ms
# - CLS < 0.1
```

### Error Monitoring

```bash
# Check error logs
tail -f /var/log/application.log | grep ERROR

# Check error tracking service
# - Sentry
# - LogRocket
# - DataDog
```

### User Feedback

- [ ] Monitor help desk tickets
- [ ] Check user feedback channels
- [ ] Review social media mentions
- [ ] Monitor support emails

### Metrics to Monitor

| Metric | Alert Threshold | Current |
|--------|-----------------|---------|
| API Error Rate | > 1% | TBD |
| Page Load Time | > 5s | TBD |
| SSE Disconnect Rate | > 5% | TBD |
| Memory Usage | > 500MB | TBD |
| CPU Usage | > 80% | TBD |

---

## Documentation After Deployment

### User Documentation
- User Guide PDF
- Video Tutorials
- FAQ page
- Keyboard Shortcuts reference
- Accessibility guide

### Developer Documentation
- API reference
- Component library docs
- Setup guide
- Architecture decision records (ADRs)
- Troubleshooting guide

### Operations Documentation
- Deployment runbook
- Incident response guide
- Scaling guide
- Backup and recovery procedures
- Monitoring and alerting setup

---

## Version Control and Releases

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-diagram-type

# Commit changes
git commit -m "feat: add new diagram type support"

# Create pull request
gh pr create --title "Add new diagram type support"

# After review, merge to main
git merge feature/new-diagram-type

# Tag release
git tag -a v1.1.0 -m "Release v1.1.0"
```

### Release Checklist
- [ ] All tests passing
- [ ] All code reviewed
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version number bumped
- [ ] Release notes written
- [ ] Security scan completed
- [ ] Performance baseline established

### CHANGELOG Entry
```markdown
## [1.0.0] - 2024-01-15

### Added
- Initial release of Architecture Gen Studio
- Support for Mermaid, D2, Structurizr, PlantUML diagrams
- SSE streaming for real-time updates
- Code validation and rendering
- Theme support

### Changed
- N/A

### Fixed
- N/A

### Security
- All dependencies updated to latest secure versions
```

---

## Post-Deployment Support

### Known Issues
- Document any known limitations
- Track resolution status
- Communicate timeline to users

### Support Channels
- Email support
- Help documentation
- FAQ page
- Chat support (if available)

### Feedback Collection
- In-app feedback button
- User surveys
- Usage analytics
- Error tracking

---

## Success Criteria

Deployment is considered successful when:

✅ All functional tests passing
✅ No critical errors in monitoring
✅ Page load time < 3 seconds
✅ API responses < 5 seconds
✅ Error rate < 0.1%
✅ User adoption > 80%
✅ No security vulnerabilities
✅ Performance metrics met
✅ All documentation complete
✅ User feedback positive

---

## Rollback Criteria

Rollback is triggered if:

❌ Error rate > 5%
❌ Page load time > 10 seconds
❌ API timeout rate > 10%
❌ Critical security vulnerability found
❌ Data corruption detected
❌ Service unavailability > 1 hour
❌ Major feature broken
❌ User complaints > 50

---

## Next Steps

1. **Day 1-7 (Monitoring)**
   - Intensive monitoring
   - Quick fix deployment for any issues
   - User feedback collection

2. **Week 2-4 (Stabilization)**
   - Performance optimization
   - Bug fix releases
   - Feature enhancements based on feedback

3. **Month 2+ (Growth)**
   - New features
   - Analytics and insights
   - Continuous improvement

---

## Contact Information

- **Product Owner:** [Name, email]
- **Tech Lead:** [Name, email]
- **DevOps:** [Name, email]
- **Support:** support@example.com
- **Emergency:** emergency@example.com

---

## Appendix: Scripts and Commands

```bash
# Development
npm start                   # Start dev server
npm test                    # Run tests
npm run build              # Build for production
npm run build:analyze      # Analyze bundle size
npm run lint               # Run linter
npm run format             # Format code
npm run type-check         # Check TypeScript

# Deployment
npm run deploy:staging     # Deploy to staging
npm run deploy:prod        # Deploy to production
npm run deploy:rollback    # Rollback to previous

# Monitoring
npm run logs:staging       # View staging logs
npm run logs:prod          # View production logs
npm run metrics:prod       # View production metrics

# Cleanup
npm run clean              # Clean build artifacts
npm run cache:clear        # Clear caches
npm audit fix              # Fix vulnerabilities
```

---

Last Updated: [Date]
Next Review: [Date]
