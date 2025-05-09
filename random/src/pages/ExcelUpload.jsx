import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useEventContext } from '../context/eventContext';
import axios from 'axios';

const ExcelUpload = () => {
    const { eventId: routeEventId } = useParams();
    const { eventId } = useEventContext();

    const [eventData, setEventData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [file, setFile] = useState(null);

    useEffect(() => {
        const fetchEventData = async () => {
        try {
            // TODO: CHANGE THE URL
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
            <h2>Dashboard for Event ID: {eventId}</h2>

            {eventData ? (
            <div>
                <h3>Event Data</h3>
                <pre>{JSON.stringify(eventData, null, 2)}</pre>
            </div>
            ) : (
            <div>
                <h3>No data found for this event. Please upload a file:</h3>
                <input type="file" onChange={handleFileChange} />
                <button onClick={handleFileUpload}>Upload File</button>
            </div>
            )}
        </div>
        );
    };

export default ExcelUpload;