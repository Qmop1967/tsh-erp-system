# TSH ERP System - Frontend

A modern React-based admin dashboard for the TSH ERP System with role-based permissions, authentication, and comprehensive management interfaces.

## Features

### 🔐 Authentication & Authorization
- Secure login with JWT tokens
- Role-based access control (RBAC)
- Protected routes and components
- Permission-based UI rendering

### 🎨 Modern UI/UX
- Responsive design with Tailwind CSS
- Dark/Light mode support
- Beautiful component library with Radix UI
- Consistent design system
- RTL support for Arabic content

### 📊 Admin Dashboard
- Real-time statistics and metrics
- Interactive charts and graphs
- Quick action cards
- System health monitoring

### 👥 User Management
- User creation, editing, and deletion
- Role and permission assignment
- User activity tracking
- Bulk operations

### 🏢 Organization Management
- **Branches**: Manage branch locations and information
- **Warehouses**: Inventory location management
- **Departments**: Organizational structure

### 📦 Inventory Management
- **Items**: Product catalog management
- **Categories**: Hierarchical categorization
- **Stock**: Real-time inventory tracking
- **Price Lists**: Dynamic pricing management

### 🤝 Relationship Management
- **Customers**: Customer information and history
- **Vendors**: Supplier management
- **Contacts**: Centralized contact management

### 🔄 Data Migration
- **Zoho Integration**: Import from Zoho Books & Inventory
- **Batch Processing**: Manage large data imports
- **Progress Tracking**: Real-time migration status
- **Error Handling**: Comprehensive error reporting

## Technology Stack

### Core Framework
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server

### State Management
- **Zustand** - Lightweight state management
- **React Query** - Server state management
- **React Hook Form** - Form state management

### UI Components
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Headless component primitives
- **Lucide React** - Icon library
- **React Hot Toast** - Notifications

### Routing & Navigation
- **React Router DOM** - Client-side routing
- **Protected Routes** - Authentication guards

### Data Validation
- **Zod** - Schema validation
- **React Hook Form Resolvers** - Form validation

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ui/           # Base UI components
│   │   ├── layout/       # Layout components
│   │   └── auth/         # Authentication components
│   ├── pages/            # Page components
│   │   ├── auth/         # Authentication pages
│   │   ├── dashboard/    # Dashboard page
│   │   ├── users/        # User management
│   │   ├── branches/     # Branch management
│   │   ├── warehouses/   # Warehouse management
│   │   ├── inventory/    # Inventory management
│   │   ├── customers/    # Customer management
│   │   ├── vendors/      # Vendor management
│   │   └── migration/    # Data migration
│   ├── stores/           # Zustand stores
│   ├── lib/              # Utilities and API clients
│   ├── types/            # TypeScript type definitions
│   └── hooks/            # Custom React hooks
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation Steps

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler

## API Integration

The frontend communicates with the FastAPI backend through:

- **Authentication API** - Login, logout, token refresh
- **Users API** - User management operations
- **Branches API** - Branch management
- **Warehouses API** - Warehouse operations
- **Items API** - Inventory management
- **Customers API** - Customer operations
- **Vendors API** - Vendor management
- **Migration API** - Data import/export

### API Configuration

The API client is configured in `src/lib/api.ts` with:
- Automatic token injection
- Request/response interceptors
- Error handling
- Base URL configuration

## Authentication Flow

1. **Login**: User provides credentials
2. **Token Storage**: JWT stored in local storage
3. **Route Protection**: Protected routes check authentication
4. **API Requests**: Automatic token injection
5. **Token Refresh**: Automatic renewal before expiration
6. **Logout**: Clear tokens and redirect

## Permission System

### Role-Based Access Control
- **Admin**: Full system access
- **Manager**: Branch/warehouse management
- **User**: Limited access to assigned modules

### Permission Checking
```typescript
// Component level
<ProtectedRoute requiredPermissions={['users.view']}>
  <UsersPage />
</ProtectedRoute>

// Hook level
const { hasPermission } = usePermissions()
if (hasPermission('users.create')) {
  // Show create button
}
```

## Theming & Customization

### Color System
The application uses a semantic color system defined in CSS variables:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96%;
  --accent: 210 40% 96%;
  --destructive: 0 84.2% 60.2%;
  /* ... */
}
```

### Dark Mode
Toggle dark mode using the header button. The theme is persisted in local storage.

### RTL Support
The application supports Arabic RTL layout:

```css
.rtl {
  direction: rtl;
}
```

## Performance Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Lazy Loading**: Components loaded on demand
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: For large data sets
- **Image Optimization**: Responsive images with lazy loading

## Development Guidelines

### Component Structure
```typescript
// Component template
interface Props {
  // Define props
}

export function Component({ prop }: Props) {
  // Hooks
  // State
  // Effects
  // Handlers
  
  return (
    // JSX
  )
}
```

### State Management
- Use Zustand for global state
- Use React Query for server state
- Use useState for local component state
- Use useForm for form state

### Error Handling
- Use React Query error boundaries
- Show user-friendly error messages
- Log errors for debugging

## Deployment

### Production Build
```bash
npm run build
```

### Environment Variables
Create `.env.production`:
```
VITE_API_URL=https://api.tsh-erp.com
VITE_APP_NAME=TSH ERP System
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Follow coding standards**: Use TypeScript, ESLint, Prettier
4. **Write tests**: Unit tests for components
5. **Submit pull request**: With detailed description

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- **Email**: support@tsh-erp.com
- **Documentation**: [docs.tsh-erp.com](https://docs.tsh-erp.com)
- **Issues**: GitHub Issues
