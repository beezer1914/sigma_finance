import { Link } from 'react-router-dom';
import useAuthStore from '../stores/authStore';

function Header({ onLogout }) {
  const { user } = useAuthStore();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">Sigma Finance</h1>
            </Link>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              to="/dashboard"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              Dashboard
            </Link>

            {user?.role === 'treasurer' && (
              <>
                <Link
                  to="/treasurer"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Treasurer
                </Link>
                <Link
                  to="/members"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Members
                </Link>
                <Link
                  to="/reports"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Reports
                </Link>
              </>
            )}
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <Link
              to="/profile"
              className="hidden sm:flex items-center space-x-3 hover:bg-gray-50 px-3 py-2 rounded-lg transition-colors"
            >
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-bold text-blue-600">
                {user?.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
              </div>
            </Link>

            <button
              onClick={onLogout}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
