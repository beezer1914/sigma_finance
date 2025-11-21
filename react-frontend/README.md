# Sigma Finance React Frontend

This is the React frontend for the Sigma Finance application, built with Vite, React 19, and Tailwind CSS.

## Tech Stack

- **React 19.2.0** - UI framework
- **Vite 7.2.2** - Build tool and dev server
- **React Router 7** - Client-side routing
- **Zustand** - State management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework

## Project Structure

```
react-frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Login.jsx         # Login page
│   │   ├── Register.jsx      # Registration page
│   │   ├── Dashboard.jsx     # Member dashboard
│   │   └── ProtectedRoute.jsx # Route protection wrapper
│   ├── stores/               # Zustand state stores
│   │   └── authStore.js      # Authentication state
│   ├── services/             # API services
│   │   └── api.js            # API client and endpoints
│   ├── App.jsx               # Main app component with routing
│   ├── main.jsx              # App entry point
│   └── index.css             # Global styles with Tailwind
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind CSS configuration
└── package.json              # Dependencies
```

## Development Setup

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Flask backend running on `http://localhost:5000`

### Installation

```bash
cd react-frontend
npm install
```

### Running the Development Server

1. **Start the Flask backend first:**
   ```bash
   # From the root directory
   python sigma_finance/app.py
   ```

2. **Start the React development server:**
   ```bash
   # From the react-frontend directory
   npm run dev
   ```

3. **Access the application:**
   - React frontend: http://localhost:5173
   - Flask backend: http://localhost:5000

The Vite dev server is configured to proxy all `/api` requests to the Flask backend at `http://localhost:5000`.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features Implemented (Phase 1)

### Authentication
- ✅ Login with email and password
- ✅ Registration with invite code
- ✅ Session-based authentication
- ✅ Protected routes
- ✅ Auto-redirect on auth state change

### Dashboard
- ✅ View user information
- ✅ Display active payment plan with progress
- ✅ Show recent payments
- ✅ Logout functionality

### Form Validation
- ✅ Client-side validation with Zod schemas
- ✅ Real-time error messages
- ✅ Server-side error handling

## API Endpoints Used

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/register` - Register new user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/user` - Get current user

### Dashboard
- `GET /api/dashboard` - Get dashboard data (payments, plan, status)

## State Management

The app uses Zustand for lightweight state management:

- **authStore** - Manages authentication state
  - `user` - Current user object
  - `isAuthenticated` - Authentication status
  - `isLoading` - Loading state
  - `error` - Error messages
  - `login()` - Login action
  - `register()` - Register action
  - `logout()` - Logout action
  - `initializeAuth()` - Check existing session

## Routing

- `/login` - Public login page
- `/register` - Public registration page
- `/dashboard` - Protected member dashboard
- `/` - Redirects to dashboard (or login if not authenticated)

## Next Steps (Future Phases)

### Phase 2: Core Features
- [ ] Payment forms (one-time, installment, plan enrollment)
- [ ] Payment history page with pagination
- [ ] Donation form
- [ ] Stripe integration

### Phase 3: Treasurer Features
- [ ] Treasurer dashboard
- [ ] Member management
- [ ] Payment management
- [ ] Donation management

### Phase 4: Reports
- [ ] Various reports (dues paid, payment plans, donations)
- [ ] CSV export functionality

### Phase 5: Production
- [ ] Build configuration
- [ ] Serve React app from Flask
- [ ] Environment configuration
- [ ] Error boundaries
- [ ] Loading states and skeletons
- [ ] Toast notifications

## Notes

- The React app runs on port 5173 in development
- API calls are proxied to Flask backend on port 5000
- Session cookies are shared between React dev server and Flask
- All API routes are exempted from CSRF protection in Flask
- Tailwind CSS classes are used for styling
