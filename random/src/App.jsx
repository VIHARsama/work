import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { EventProvider } from './context/eventContext';
import Dashboard from './pages/Dashboard';
import CreateEvent from './pages/createEvent';
import ProtectedRoute from './authentication/protectedRoute';

function App() {
  return (
    <EventProvider>
      <Router>
        <Routes>
          <Route path="/create-event" element={<CreateEvent />} />
          <Route
            path="/:eventId"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </EventProvider>
  );
}

export default App;