import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useEventContext } from '../context/eventContext';
import axios from 'axios';

const Dashboard = () => {
    const { eventId: routeEventId } = useParams();
    const { eventId } = useEventContext();

    const [eventData, setEventData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [file, setFile] = useState(null);

    useEffect(() => {
        const fetchEventData = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/api/get-santa-pairs/?eventID=${eventId}`);
            
            if (response.status === 200 && response.data) {
            setEventData(response.data);
            }
        } catch (err) {
            console.log(err)
            setError('Failed to load event data');
        } finally {
            setLoading(false);
        }
        };
        fetchEventData();
    }, [routeEventId]);

    if (loading) {
        return <div>Loading...</div>;
      }
    
      if (error) {
        return <div>{error}</div>;
      }


    return (
        <div>
            {eventData ? (
                eventData.santaPairs && eventData.santaPairs.length > 0 ? (
                <div>
                    <h3>Event Data</h3>
                    <pre>{JSON.stringify(eventData, null, 2)}</pre>
                </div>
                ) : (
                <div>
                    <h3>No Santa Pairs Found</h3>
                </div>
                )
            ) : (
                <div>
                <h3>No Data</h3>
                </div>
            )}
        </div>
        );
    };

export default Dashboard;