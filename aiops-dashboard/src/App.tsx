import { useState } from 'react';
import { Dashboard } from './pages/Dashboard';
import { Login } from './pages/Login';

function App() {
  // Simple auth state - default to logged in for demo
  const [token, setToken] = useState<string | null>('demo-token');

  // We're not persisting user details in this simple version, 
  // but in a real app you'd store them or fetch /me

  const handleLoginSuccess = (newToken: string, _newUser: any) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  if (!token) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return <Dashboard onLogout={handleLogout} />;
}

export default App;
