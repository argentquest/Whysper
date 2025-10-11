# How to Use C4 Diagrams in Whysper

## ⚠️ Important: How Diagram Rendering Works

**Diagrams are rendered from the AI's response, NOT from user input!**

### ❌ This Won't Work:
```
[You paste C4 code into chat]
User: C4Container
      Person(user, "User")
      System(app, "App")

Result: AI explains the code, doesn't render it
```

### ✅ This Will Work:
```
[You ask the AI to create a diagram]
User: Create a C4 container diagram showing a web app with a database

AI Response: Here's your C4 diagram:
```c4
C4Container
Person(user, "User")
Container(app, "Web App", "React")
ContainerDb(db, "Database", "PostgreSQL")
Rel(user, app, "Uses")
Rel(app, db, "Queries")
```

Result: Beautiful rendered diagram! 🎉
```

---

## 🎯 How to Get C4 Diagrams

### **Method 1: Ask for Specific C4 Levels**

**Context Diagram (Level 1):**
```
Create a C4 Context diagram for a payment processing system with:
- Customer as the user
- Payment System as the main system
- Bank API as an external system
```

**Container Diagram (Level 2):**
```
Create a C4 Container diagram showing a web application with:
- Load Balancer (Nginx)
- 3 Application Servers (Java/Spring)
- Redis Cache
- MySQL Database
```

**Component Diagram (Level 3):**
```
Create a C4 Component diagram for an API Gateway with:
- API Controller
- Authentication Service
- Payment Gateway Adapter
```

### **Method 2: Use Test Prompts**

Use the test prompts from [backend/tests/Diagrams/test.json](backend/tests/Diagrams/test.json):

```
Generate a **C4 Component Diagram** showing the internal components of the 'Web Application' (from the previous prompt). Include 'Authentication Service', 'Payment Gateway Adapter', and 'API Controller'. Show how the 'API Controller' uses the other two services.
```

### **Method 3: Ask for System_Boundary**

```
Create a C4 Container diagram with a System_Boundary for "Payment Processing System" containing:
- Load Balancer
- 3 App Servers
- Redis Cache
- MySQL Database

Show a User outside the boundary accessing the system via HTTPS.
```

---

## 🔍 What Happens When You Ask

1. **You send your request** to the AI
2. **AI generates C4 code** in its response
3. **Frontend detects C4 syntax** in the AI's message
4. **C4-to-D2 translator** converts the code
5. **D2 renderer** creates beautiful SVG
6. **You see the diagram!** 🎉

---

## 📝 Example Conversation

**You:**
> Create a C4 Container diagram for an e-commerce system with:
> - Web frontend (React)
> - Mobile app (React Native)
> - API Gateway (Node.js)
> - Product Service (Java)
> - User Service (Python)
> - PostgreSQL database
> - Redis cache

**AI Response:**
```c4
C4Container
title E-Commerce System - Container Diagram

Person(customer, "Customer", "Online shopper")

Container(web, "Web Frontend", "React", "Customer web interface")
Container(mobile, "Mobile App", "React Native", "iOS and Android app")
Container(api, "API Gateway", "Node.js", "Routes requests")
Container(productSvc, "Product Service", "Java", "Manages products")
Container(userSvc, "User Service", "Python", "Manages users")
ContainerDb(db, "Database", "PostgreSQL", "Stores data")
ContainerDb(cache, "Cache", "Redis", "Caches data")

Rel(customer, web, "Browses", "HTTPS")
Rel(customer, mobile, "Uses", "HTTPS")
Rel(web, api, "API Calls", "JSON/HTTPS")
Rel(mobile, api, "API Calls", "JSON/HTTPS")
Rel(api, productSvc, "Product requests")
Rel(api, userSvc, "User requests")
Rel(productSvc, db, "Reads/Writes", "SQL")
Rel(userSvc, db, "Reads/Writes", "SQL")
Rel(productSvc, cache, "Caches", "Redis Protocol")
Rel(userSvc, cache, "Caches", "Redis Protocol")
```

**Result:** Beautiful C4 diagram rendered with D2! ✨

---

## 🎨 What You'll See

When the AI responds with C4 code, you'll see:

1. **Card Title:** "C4 Architecture Diagram"
2. **Purple Tag:** "[C4 Container]" (shows the level)
3. **Blue Tag:** "[Rendered with D2]"
4. **Buttons:**
   - Copy C4 - Copy original C4 source
   - Show/Hide D2 - Toggle D2 code preview
   - Copy D2 - Copy generated D2 code
   - SVG - Download vector
   - PNG - Download raster
5. **Beautiful Diagram:** Rendered with D2's professional layout

---

## 🏗️ Supported C4 Features

### **Levels:**
- ✅ C4Context - System context
- ✅ C4Container - Technology containers
- ✅ C4Component - Internal components
- ✅ C4Dynamic - Flow diagrams
- ✅ C4Deployment - Deployment architecture

### **Entities:**
- ✅ Person / Person_Ext
- ✅ System / System_Ext / SystemDb / SystemQueue
- ✅ Container / Container_Ext / ContainerDb / ContainerQueue
- ✅ Component / Component_Ext / ComponentDb / ComponentQueue

### **Boundaries:**
- ✅ System_Boundary(id, "label") { ... }
- ✅ Enterprise_Boundary(id, "label") { ... }
- ✅ Container_Boundary(id, "label") { ... }

### **Relationships:**
- ✅ Rel(from, to, "label")
- ✅ Rel(from, to, "label", "technology")

---

## 💡 Pro Tips

### **Be Specific:**
Instead of: "Create a C4 diagram"
Say: "Create a C4 Container diagram for a payment system with a load balancer, 3 app servers, and a database"

### **Use the Right Level:**
- **Context** - For system boundaries and external actors
- **Container** - For technology stack (apps, databases, services)
- **Component** - For internal architecture (controllers, services, adapters)

### **Ask for Boundaries:**
"Create a C4 diagram with a System_Boundary grouping the internal components"

### **Iterate:**
If the diagram isn't quite right, ask:
"Add a Redis cache to the diagram"
"Show the Mobile App connecting to the API Gateway"
"Group the App Servers inside a boundary"

---

## 🐛 Troubleshooting

### **Issue: AI Just Explains the Code**
**Cause:** You pasted C4 code instead of asking for it
**Solution:** Ask the AI to create the diagram, don't paste code yourself

### **Issue: No Diagram Appears**
**Cause:** AI didn't wrap code in ````c4` or ````mermaid` block
**Solution:** Ask: "Can you put that in a C4 code block so it renders?"

### **Issue: Wrong Diagram Type**
**Cause:** AI used Mermaid or D2 instead of C4
**Solution:** Be explicit: "Create a **C4 Container** diagram with..."

### **Issue: Boundary Not Showing**
**Cause:** AI didn't use System_Boundary syntax
**Solution:** Ask: "Can you put those components inside a System_Boundary?"

---

## 📚 Example Prompts

### **Simple Context Diagram:**
```
Create a C4 Context diagram for a blog platform showing:
- Authors who write posts
- The Blog System
- External Email Service for notifications
```

### **Container with Technology:**
```
Create a C4 Container diagram for a microservices architecture with:
- API Gateway (Kong)
- Auth Service (Node.js)
- Content Service (Go)
- MongoDB database
- Kafka message broker
```

### **Component Diagram:**
```
Create a C4 Component diagram for the Auth Service showing:
- REST Controller
- JWT Service
- Password Hasher
- User Repository
- Redis Session Store
```

### **With Boundary:**
```
Create a C4 Container diagram with a System_Boundary called "Backend Services" containing:
- API Gateway
- 3 Microservices
- Message Queue
Show a mobile app outside the boundary connecting to the API Gateway
```

---

## ✅ Summary

**Remember:**
1. ❌ **Don't paste C4 code** - AI won't render it
2. ✅ **Ask AI to create diagram** - It will respond with code that renders
3. 🎨 **Be specific** - Mention C4 level, components, relationships
4. 🏗️ **Use boundaries** - Ask for System_Boundary to group components
5. 🔄 **Iterate** - Ask AI to modify the diagram if needed

**The key:** Diagrams render from **AI responses**, not user input!

---

## 🎯 Quick Start

**Right now, try this:**

```
Create a C4 Container diagram for a payment processing system with:
- User (Person)
- System_Boundary containing:
  - Load Balancer (Nginx)
  - 3 Application Servers (Java/Spring)
  - Redis Cache (Redis)
  - SQL Database (MySQL)
- Show the user accessing the load balancer via HTTPS
- Show the app servers reading from Redis and writing to the database
```

**That's it!** The AI will respond with a C4 diagram that automatically renders with D2! 🚀
