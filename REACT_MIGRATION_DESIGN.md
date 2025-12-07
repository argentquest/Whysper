# React Migration Design Document

## 1. Executive Summary

This document serves as the technical blueprint for migrating the InkAndQuill frontend from server-side rendered Jinja2 templates to a modern React Single Page Application (SPA). The goal is to decouple the frontend from the backend, improve user experience with real-time interactivity, and adopt a scalable architecture using **React, TypeScript, and Ant Design**.

**Scope:**
- Replacement of all Jinja2 views with React pages.
- Implementation of the Ant Design component library.
- Mapping of existing data injection (Jinja Context) to API calls.

---

## 2. Current Architecture & Jinja Interaction Map

The current application uses `FastAPI` + `Jinja2` to render HTML on the server. Data is injected directly into templates via the `context` dictionary.

### 2.1 Core View Routers

The following table explicitly identifies the key interactions found in the code analysis.

| Router File | Route Path | Template | Data Context (to be replaced by API) |
|-------------|------------|----------|--------------------------------------|
| `views_world.py` | `GET /ui/worlds` | `pages/world_list.html` | `worlds` (List), `current_user` |
| `views_world.py` | `GET /ui/worlds/new` | `pages/world_form.html` | `world` (None), `form_action_url` |
| `views_world.py` | `GET /ui/worlds/{id}` | `pages/world_detail.html` | `world`, `locations`, `characters`, `lore_items` |
| `views_story_act.py` | `GET /stories` | `pages/stories_list.html` | `stories` (List), `current_user` |
| `views_story_act.py` | `GET /stories/new` | `pages/story_form.html` | `story` (None), `available_worlds` |
| `views_story_act.py` | `GET /stories/{id}` | `pages/story_detail.html` | `story`, `acts`, `scenes`, `characters` |
| `views_general.py` | `GET /login` | `pages/login.html` | `request`, `message` |
| `views_general.py` | `GET /register` | `pages/register.html` | `request`, `next_step` |
| `views_blog.py` | `GET /blog` | `blog/home_modern.html` | `posts`, `categories`, `tags`, `featured_posts` |
| `views_billing.py` | `GET /billing` | `pages/billing_dashboard.html` | `billing_data`, `total_cost`, `usage_percentage` |
| `views_prompt.py` | `GET /prompts` | `pages/prompts_list.html` | `prompts`, `filter_is_active`, `prompt_types` |
| `views_world_chat.py`| `GET /ui/world-chat/{id}` | `pages/world_chat.html` | `world`, `chat_history`, `current_user` |

### 2.2 Data Injection Pattern

Currently, the backend prepares complex objects (dictionaries/Pydantic models) and passes them to `TemplateResponse`.
*   **Legacy:** `return templates.TemplateResponse("page.html", {"data": my_object})`
*   **Target:** `GET /api/v1/resource/{id} -> JSON { "data": ... }`

---

## 3. React Component Architecture

The new frontend will be a **Single Page Application (SPA)** using `React Router` for navigation.

### 3.1 Global Layout (`MainLayout.tsx`)
Replaces `base.html` and `dashboard_base.html`.
- **Ant Design Components:** `Layout`, `Sider`, `Header`, `Content`, `Footer`.
- **Features:** Responsive Sidebar, Top Navigation, User Dropdown, Theme Toggle.

### 3.2 Page Component Mapping

| Legacy Template | New React Component | Ant Design Components |
|-----------------|---------------------|-----------------------|
| `pages/world_list.html` | `WorldListPage.tsx` | `Table`, `Card` (Grid view), `Button` (Create) |
| `pages/world_form.html` | `WorldFormPage.tsx` | `Form`, `Input`, `Select`, `Upload` (Cover Image) |
| `pages/world_detail.html`| `WorldDetailPage.tsx`| `Descriptions`, `Tabs` (Locations/Chars), `List` |
| `pages/story_detail.html`| `StoryDetailPage.tsx`| `Tree` (Act/Scene structure), `Drawer` (Edit Scene) |
| `pages/login.html` | `LoginPage.tsx` | `Form`, `Input.Password`, `Button`, `Alert` (Errors) |
| `pages/billing_dashboard.html` | `BillingPage.tsx` | `Statistic`, `Progress` (Usage), `Table` (Invoices) |
| `pages/world_chat.html` | `WorldChatPage.tsx` | `List` (Messages), `Input.TextArea`, `Avatar` |

---

## 4. Migration Strategy: Interactions & APIs

### 4.1 Authentication
- **Current:** Session-based (Cookies) handled by FastAPI middlewares.
- **New:** JWT (JSON Web Tokens).
    - **Login:** `POST /api/v1/auth/token` -> Returns `{ access_token }`.
    - **Storage:** Store token in `localStorage` or `httpOnly` cookie.
    - **Interceptor:** Add `Authorization: Bearer <token>` to all Axios/Fetch requests.

### 4.2 Data Fetching (TanStack Query)
Replace direct Jinja context with asynchronous hooks.

**Example: World Detail**
*   **Old:** `views_world.py` fetches `world`, `locations`, `characters` and renders HTML.
*   **New:**
    1.  `WorldDetailPage` mounts.
    2.  `useQuery(['world', id], () => fetchWorld(id))` fires.
    3.  `useQuery(['worldLocations', id], () => fetchLocations(id))` fires in parallel.
    4.  Components render `Skeleton` loaders while fetching.
    5.  Data populates the UI.

### 4.3 Form Submission
- **Current:** Standard HTML Forms (`<form action="..." method="post">`). Browser reloads page.
- **New:** React `onSubmit` handlers.
    - Prevent default behavior.
    - Collect data using `Ant Form`.
    - `POST /api/v1/...` using Axios.
    - On success: `notification.success()`, then `navigate()`.
    - On error: `notification.error()`, highlight form fields.

---

## 5. Detailed Component Design Examples

### 5.1 World List (`WorldListPage.tsx`)
**Interaction:** Fetch list of worlds.
```tsx
const columns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Genre', dataIndex: 'genre', key: 'genre' },
  { title: 'Actions', render: (_, record) => <Link to={`/worlds/${record.id}`}>View</Link> }
];

return <Table dataSource={data} columns={columns} loading={isLoading} />;
```

### 5.2 Story Editor (Complex Interaction)
**Old:** `basic_story_editor.html` (Jinja + Vanilla JS + WebSocket).
**New:** `StoryEditorPage.tsx`
- **Layout:** `Splitter` (AntD 5.21+) for resizable panes (Sidebar / Editor / Chat).
- **Editor:** `RichTextEditor` (e.g., Quill or Tiptap) wrapped in a custom component.
- **State:** `useStoryStore` (Zustand) to manage Act/Scene active state.
- **WebSocket:** `useWebSocket` hook to listen for AI generation events.

---

## 6. Implementation Phases

1.  **Phase 1: Foundation**
    - Setup Vite + React + TypeScript.
    - Configure Ant Design Theme.
    - Setup Axios & React Query.
    - Implement Auth Layout & Login Page.

2.  **Phase 2: Core CRUD Entities**
    - Worlds, Characters, Locations.
    - Implement List, Detail, and Form views.

3.  **Phase 3: Story Engine**
    - Story management.
    - Complex nested structures (Act -> Scene).

4.  **Phase 4: Real-time Features**
    - Chat interfaces.
    - WebSocket integration for AI generation.

5.  **Phase 5: Cleanup**
    - Remove Jinja routers (`views_*.py`).
    - Remove `templates/` directory.
