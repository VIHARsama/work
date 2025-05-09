import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useEventContext } from '../context/eventContext';

const CreateEvent = () => {
  const [eventIdInput, setEventIdInput] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useEventContext();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/create-event/', {
        eventID: eventIdInput,
        password,
      });

      if (response.status === 200 || response.status === 201) {
        login(eventIdInput); 
        navigate(`/${eventIdInput}`);
      }
    } catch (error) {
      alert('Invalid event ID or password');
      console.error(error);
    } finally {
      setLoading(false);  // Set loading to false once the request completes (either success or failure)
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Event ID"
        value={eventIdInput}
        onChange={(e) => setEventIdInput(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating Event...' : 'Create Event'}
      </button>
    </form>
  );
};

export default CreateEvent;