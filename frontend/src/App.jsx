import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [transactions, setTransactions] = useState([]);
  const [chartData, setChartData] = useState([]);

  // Simülasyon: Gerçek bir WebSocket yerine şimdilik test amaçlı sahte veri ekleyelim
  useEffect(() => {
    const interval = setInterval(() => {
      const isFraud = Math.random() > 0.8;
      const newTx = {
        id: Math.random().toString(36).substr(2, 9),
        user: `user_${Math.floor(Math.random() * 5) + 1}`,
        amount: Math.floor(Math.random() * 500) + 10,
        status: isFraud ? 'FRAUD' : 'APPROVED',
        time: new Date().toLocaleTimeString(),
      };

      setTransactions(prev => [newTx, ...prev].slice(0, 10)); // Son 10 işlem
      
      setChartData(prev => {
        const newData = [...prev, { time: newTx.time, amount: newTx.amount }];
        return newData.slice(-15); // Grafikte son 15 nokta
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Fraud Shield Dashboard</h1>
      
      <div style={{ display: 'flex', gap: '20px' }}>
        {/* Sol Panel: Canlı Akış */}
        <div style={{ flex: 1, border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
          <h3>Canlı İşlem Akışı</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {transactions.map(tx => (
              <li key={tx.id} style={{ 
                padding: '10px', 
                marginBottom: '5px', 
                backgroundColor: tx.status === 'FRAUD' ? '#ffebee' : '#e8f5e9',
                borderLeft: `5px solid ${tx.status === 'FRAUD' ? 'red' : 'green'}`
              }}>
                <strong>{tx.user}</strong> - ${tx.amount} ({tx.time})
                <span style={{ float: 'right', fontWeight: 'bold', color: tx.status === 'FRAUD' ? 'red' : 'green' }}>
                  {tx.status}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Sağ Panel: Grafik */}
        <div style={{ flex: 1, border: '1px solid #ccc', padding: '10px', borderRadius: '8px' }}>
          <h3>İşlem Hacmi (Zaman)</h3>
          <div style={{ width: '100%', height: '300px' }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="amount" stroke="#8884d8" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
