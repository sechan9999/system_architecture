
import React, { useState } from 'react';
import {
  LayoutDashboard,
  Activity,
  Server,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Search,
  CheckCircle,
  XCircle,
  BarChart3,
  Globe
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { analyzeClaim, MOCK_TEMPLATES } from './mockLogic';

const COLORS = ['#22c55e', '#eab308', '#f97316', '#ef4444'];
const RISK_DATA = [
  { name: 'Low', value: 900 },
  { name: 'Medium', value: 250 },
  { name: 'High', value: 80 },
  { name: 'Critical', value: 20 },
];
const AGENT_DATA = [
  { name: 'Statistical', value: 15 },
  { name: 'ML Pattern', value: 25 },
  { name: 'Rule Comp', value: 40 },
  { name: 'Features', value: 10 },
  { name: 'Graph', value: 10 },
];

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo-area">
          <div className="logo-icon"><ShieldCheck size={20} /></div>
          <span className="logo-text">Compound AI</span>
        </div>

        <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
          <LayoutDashboard size={18} /> Dashboard
        </div>
        <div className={`nav-item ${activeTab === 'analysis' ? 'active' : ''}`} onClick={() => setActiveTab('analysis')}>
          <Search size={18} /> Real-time Analysis
        </div>
        <div className={`nav-item ${activeTab === 'health' ? 'active' : ''}`} onClick={() => setActiveTab('health')}>
          <Activity size={18} /> System Health
        </div>

        <div style={{ marginTop: 'auto', padding: '10px', fontSize: '0.8rem', color: '#64748b' }}>
          v1.2.0 • GitHub Pages Build
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {activeTab === 'dashboard' && <DashboardView />}
        {activeTab === 'analysis' && <AnalysisView />}
        {activeTab === 'health' && <HealthView />}
      </div>
    </div>
  );
}

const DashboardView = () => (
  <>
    <div style={{ marginBottom: '30px' }}>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Fraud Detection Overview</h1>
      <p style={{ color: '#94a3b8' }}>Real-time monitoring of insurance claims processing</p>
    </div>

    <div className="grid-container">
      <MetricCard title="Total Analyzed" value="1,250" delta="+25 today" isPositive={true} />
      <MetricCard title="Fraud Detected" value="45" delta="+2 today" isPositive={false} isInverse={true} />
      <MetricCard title="Pending Review" value="12" delta="-5 from yesterday" isPositive={true} />
      <MetricCard title="Potential Savings" value="$450k" delta="+$15k this week" isPositive={true} />
    </div>

    <div className="charts-grid">
      <div className="chart-card">
        <div className="chart-header">
          <div className="chart-title">Risk Distribution</div>
        </div>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={RISK_DATA}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {RISK_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                itemStyle={{ color: '#f8fafc' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <div className="chart-title">Agent Anomaly Detection Rate</div>
        </div>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={AGENT_DATA}>
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  </>
);

const AnalysisView = () => {
  const [formData, setFormData] = useState(MOCK_TEMPLATES["Normal Claim"]);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleTemplateChange = (e) => {
    const t = MOCK_TEMPLATES[e.target.value];
    if (t) setFormData(t);
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setResult(null);
    const res = await analyzeClaim(formData);
    setResult(res);
    setAnalyzing(false);
  };

  return (
    <>
      <div style={{ marginBottom: '30px' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 700 }}>Analysis Workbench</h1>
        <p style={{ color: '#94a3b8' }}>Run multi-agent analysis on individual claims</p>
      </div>

      <div className="split-layout">
        <div className="form-panel">
          <div className="form-group">
            <label className="form-label">Template</label>
            <select className="form-select" onChange={handleTemplateChange}>
              <option>Normal Claim</option>
              <option>Suspicious (High Amount)</option>
              <option>Fraud (Sanctioned Provider)</option>
            </select>
          </div>

          <div style={{ height: '1px', background: '#334155', margin: '20px 0' }}></div>

          <div className="form-group">
            <label className="form-label">Claim ID</label>
            <input className="form-input" value={formData.claimId} onChange={(e) => setFormData({ ...formData, claimId: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Provider ID</label>
            <input className="form-input" value={formData.providerId} onChange={(e) => setFormData({ ...formData, providerId: e.target.value })} />
          </div>
          <div className="form-group">
            <label className="form-label">Amount ($)</label>
            <input type="number" className="form-input" value={formData.amount} onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })} />
          </div>
          <div className="form-group">
            <label className="form-label">Procedure Code</label>
            <input className="form-input" value={formData.procedureCode} onChange={(e) => setFormData({ ...formData, procedureCode: e.target.value })} />
          </div>

          <button className="btn-primary" onClick={handleAnalyze} disabled={analyzing}>
            {analyzing ? 'Processing...' : <><Search size={18} /> Analyze Claim</>}
          </button>
        </div>

        <div className="result-panel">
          {!result && !analyzing && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#64748b' }}>
              <Server size={48} style={{ opacity: 0.5, marginBottom: 20 }} />
              <p>Ready to analyze. Submit a claim to begin.</p>
            </div>
          )}

          {analyzing && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <Globe className="analyzing-text" size={48} />
              <div style={{ width: '200px', marginTop: 20 }}>
                <div style={{ textAlign: 'center', marginBottom: 5, fontSize: '0.9rem', color: '#94a3b8' }}>Coordinating Agents...</div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: '100%', animation: 'width 2s infinite' }}></div>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div style={{ animation: 'fadeIn 0.5s' }}>
              {/* Header Result */}
              <div style={{
                background: getRiskColor(result.riskLevel, 0.2),
                border: `1px solid ${getRiskColor(result.riskLevel, 0.4)}`,
                borderRadius: '8px',
                padding: '24px',
                marginBottom: '24px',
                textAlign: 'center'
              }}>
                <div style={{ color: getRiskColor(result.riskLevel, 1), fontWeight: 700, fontSize: '1.2rem', marginBottom: 8 }}>
                  {result.riskLevel.toUpperCase()} RISK
                </div>
                <div style={{ fontSize: '3rem', fontWeight: 800, lineHeight: 1, marginBottom: 12 }}>
                  {result.score.toFixed(3)}
                </div>
                <div style={{
                  background: getRiskColor(result.riskLevel, 1),
                  color: '#000',
                  display: 'inline-block',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontWeight: 600,
                  fontSize: '0.9rem'
                }}>
                  {result.action}
                </div>
              </div>

              {/* Finding Section */}
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ marginBottom: '12px', fontSize: '1rem' }}>🔑 Key Findings</h3>
                {result.keyFindings.map((f, i) => (
                  <div key={i} style={{
                    marginBottom: '8px',
                    padding: '10px',
                    background: 'rgba(234, 179, 8, 0.1)',
                    borderLeft: '3px solid #eab308',
                    borderRadius: '4px',
                    fontSize: '0.95rem'
                  }}>
                    {f}
                  </div>
                ))}
              </div>

              {/* Agents */}
              <div>
                <h3 style={{ marginBottom: '12px', fontSize: '1rem' }}>🤖 Agent Assessments</h3>
                {result.agentResults.map((agent, i) => (
                  <div key={i} className="agent-card">
                    <div className="agent-header">
                      <span className="agent-name">{agent.name}</span>
                      <span style={{ color: agent.risk > 0.5 ? '#ef4444' : '#22c55e', fontWeight: 600 }}>
                        Risk: {agent.risk.toFixed(2)}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '8px' }}>Confidence: {agent.confidence.toFixed(2)}</div>
                    {agent.findings.map((f, j) => (
                      <div key={j} className="finding-item">
                        • {f}
                      </div>
                    ))}
                  </div>
                ))}
              </div>

            </div>
          )}
        </div>
      </div>
    </>
  );
};

const HealthView = () => (
  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
    <div style={{
      width: '120px', height: '120px',
      borderRadius: '50%', background: 'rgba(34, 197, 94, 0.2)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      marginBottom: '30px'
    }}>
      <CheckCircle size={60} color="#22c55e" />
    </div>
    <h1 style={{ fontSize: '2rem', marginBottom: '10px' }}>System Operational</h1>
    <p style={{ color: '#94a3b8', marginBottom: '30px' }}>All 5 agents are active and responding</p>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', width: '600px' }}>
      <div className="metric-card" style={{ textAlign: 'center' }}>
        <div className="metric-title">Uptime</div>
        <div className="metric-value" style={{ fontSize: '1.5rem' }}>99.9%</div>
      </div>
      <div className="metric-card" style={{ textAlign: 'center' }}>
        <div className="metric-title">Latency</div>
        <div className="metric-value" style={{ fontSize: '1.5rem' }}>45ms</div>
      </div>
      <div className="metric-card" style={{ textAlign: 'center' }}>
        <div className="metric-title">Error Rate</div>
        <div className="metric-value" style={{ fontSize: '1.5rem' }}>0.01%</div>
      </div>
    </div>
  </div>
);

// Components
const MetricCard = ({ title, value, delta, isPositive, isInverse }) => {
  const isGood = isInverse ? !isPositive : isPositive;
  return (
    <div className="metric-card">
      <div className="metric-title">{title}</div>
      <div className="metric-value">{value}</div>
      <div className={`metric-delta ${isGood ? 'delta-positive' : 'delta-negative'}`}>
        {isGood ? <CheckCircle size={12} /> : <AlertTriangle size={12} />}
        {delta}
      </div>
    </div>
  );
};

const getRiskColor = (level, alpha = 1) => {
  switch (level) {
    case 'critical': return `rgba(239, 68, 68, ${alpha})`; // red
    case 'high': return `rgba(249, 115, 22, ${alpha})`; // orange
    case 'medium': return `rgba(234, 179, 8, ${alpha})`; // yellow
    case 'low': return `rgba(34, 197, 94, ${alpha})`; // green
    default: return `rgba(148, 163, 184, ${alpha})`;
  }
};

export default App;
