import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Matcher from './pages/Matcher';
import Settings from './pages/Settings';
import History from './pages/History';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        
        {/* Main App with Sidebar */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/history" element={<History />} />
        </Route>

        {/* Standalone Pages */}
        <Route path="/matcher" element={<Matcher />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
