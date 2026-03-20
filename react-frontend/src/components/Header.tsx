import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAuthStore from '../stores/authStore';

interface HeaderProps {
  onLogout: () => void;
}

function Header({ onLogout }: HeaderProps) {
  const { user } = useAuthStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const location = useLocation();

  const isActive = (path: string): boolean => location.pathname === path;

  // Role-based access helpers
  const hasFullAccess = () => ['admin', 'treasurer', 'president', 'vice_1'].includes(user?.role);
  const hasReportAccess = () => ['admin', 'treasurer', 'president', 'vice_1', 'vice_2', 'secretary'].includes(user?.role);

  const navLinks = [
    { to: '/dashboard', label: 'Dashboard', show: true },
    { to: '/payments', label: 'Payments', show: true },
    { to: '/treasurer', label: 'Treasurer', show: hasFullAccess() },
    { to: '/members', label: 'Members', show: hasFullAccess() },
    { to: '/donations', label: 'Donations', show: hasFullAccess() },
    { to: '/invites', label: 'Invites', show: hasReportAccess() },
    { to: '/reports', label: 'Reports', show: hasReportAccess() },
  ];

  const visibleLinks = navLinks.filter(link => link.show);

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-surface-border backdrop-blur-md bg-sigma-950/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="md:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-surface-hover transition-colors focus:outline-none focus:ring-2 focus:ring-royal-500"
              aria-label="Open menu"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* Logo and Brand */}
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center gap-3 group">
                <div className="w-8 h-8 rounded-lg bg-royal-600 flex items-center justify-center text-white font-heading font-bold text-sm group-hover:shadow-glow-blue transition-shadow">
                  ΣΔΣ
                </div>
                <span className="font-heading text-xl font-semibold text-white tracking-tight hidden sm:block">
                  Sigma Finance
                </span>
              </Link>
            </div>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1">
              {visibleLinks.map(link => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`nav-link ${isActive(link.to) ? 'active' : ''}`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* User Menu */}
            <div className="flex items-center gap-2 sm:gap-3">
              <Link
                to="/profile"
                className="hidden sm:flex items-center gap-3 hover:bg-surface-hover px-3 py-2 rounded-lg transition-all"
              >
                <div className="w-8 h-8 bg-royal-600/20 border border-royal-500/30 rounded-full flex items-center justify-center text-sm font-semibold text-royal-300">
                  {user?.name?.charAt(0)?.toUpperCase() || '?'}
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-200">{user?.name}</p>
                  <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                </div>
              </Link>

              <button
                onClick={onLogout}
                className="px-3 py-2 sm:px-4 text-sm font-medium text-gray-400 hover:text-white border border-surface-border hover:border-rose-500/40 hover:bg-rose-500/10 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-rose-500"
              >
                <span className="hidden sm:inline">Logout</span>
                <svg className="sm:hidden h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div
            className="modal-backdrop !items-start !justify-start"
            onClick={() => setMobileMenuOpen(false)}
          />

          {/* Slide-out drawer */}
          <div className="fixed inset-y-0 left-0 w-72 bg-sigma-900 border-r border-surface-border shadow-2xl transform transition-transform duration-300 ease-out animate-slide-in-right">
            {/* Drawer Header */}
            <div className="flex items-center justify-between h-16 px-4 border-b border-surface-border">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-royal-600 flex items-center justify-center text-white font-heading font-bold text-xs">
                  ΣΔΣ
                </div>
                <h2 className="font-heading text-lg font-semibold text-white">Menu</h2>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-2 rounded-lg text-gray-500 hover:text-white hover:bg-surface-hover transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* User Info */}
            <Link
              to="/profile"
              onClick={() => setMobileMenuOpen(false)}
              className="flex items-center gap-3 px-4 py-4 border-b border-surface-border hover:bg-surface-hover transition-colors"
            >
              <div className="w-11 h-11 bg-royal-600/20 border border-royal-500/30 rounded-full flex items-center justify-center text-base font-semibold text-royal-300">
                {user?.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
              <div>
                <p className="font-medium text-gray-200">{user?.name}</p>
                <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
              </div>
            </Link>

            {/* Navigation Links */}
            <nav className="px-3 py-4 space-y-1">
              {visibleLinks.map(link => (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                    isActive(link.to)
                      ? 'bg-royal-600/20 text-white border border-royal-500/20'
                      : 'text-gray-400 hover:text-white hover:bg-surface-hover'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>

            {/* Bottom section */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-surface-border">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onLogout();
                }}
                className="w-full px-4 py-3 text-sm font-medium text-gray-300 border border-surface-border hover:border-rose-500/40 hover:bg-rose-500/10 hover:text-white rounded-lg transition-all"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default Header;
