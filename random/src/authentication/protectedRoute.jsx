import { Navigate } from 'react-router-dom';
import { useEventContext } from '../context/eventContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useEventContext();
  return isAuthenticated ? children : <Navigate to="/create-event" />;
};

export default ProtectedRoute;