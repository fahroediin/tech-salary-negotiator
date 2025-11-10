import React from 'react';
import { TrendingUp, DollarSign, Settings, Home } from 'lucide-react';

const Header = ({ onNavigate, currentView }) => {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">
                Tech Salary Negotiator
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-6">
            <nav className="hidden md:flex space-x-6">
              <button
                onClick={() => onNavigate && onNavigate('home')}
                className={`flex items-center space-x-1 transition-colors ${
                  currentView === 'home'
                    ? 'text-blue-600 font-medium'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Home className="w-4 h-4" />
                <span>Home</span>
              </button>

              {onNavigate && (
                <button
                  onClick={() => onNavigate('umk-admin')}
                  className={`flex items-center space-x-1 transition-colors ${
                    currentView === 'umk-admin'
                      ? 'text-blue-600 font-medium'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Settings className="w-4 h-4" />
                  <span>UMK Admin</span>
                </button>
              )}

              <a href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-gray-600 hover:text-gray-900 transition-colors">
                How It Works
              </a>
              <a href="#about" className="text-gray-600 hover:text-gray-900 transition-colors">
                About
              </a>
            </nav>

            <button className="flex items-center space-x-2 bg-gray-900 text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
              <DollarSign className="w-4 h-4" />
              <span className="text-sm font-medium">Contribute Data</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;