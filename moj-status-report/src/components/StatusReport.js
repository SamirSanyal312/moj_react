import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './StatusReport.css'; // custom CSS file

function StatusReport() {
  const [data, setData] = useState({ users: 0, jokes: 0 });

  useEffect(() => {
    axios.get('http://localhost:5000/api/status')
      .then(res => setData(res.data))
      .catch(err => console.error('Error fetching status:', err));
  }, []);

  return (
    <div className="status-container">
      <h1>Status Report</h1>
      <div className="status-card">
        <div className="status-item">
          <span className="label">👤 Total Users:</span>
          <span className="value">{data.users}</span>
        </div>
        <div className="status-item">
          <span className="label">😂 Total Jokes:</span>
          <span className="value">{data.jokes}</span>
        </div>
      </div>
    </div>
  );
}

export default StatusReport;
