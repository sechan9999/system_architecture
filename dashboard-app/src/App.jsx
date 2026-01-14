
import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, Area, AreaChart } from 'recharts';
import { Shield, Activity, AlertTriangle, DollarSign, TrendingUp, TrendingDown, CheckCircle, Clock, Search, Bell, Settings, ChevronRight, Zap, Database, Network, Brain, FileText } from 'lucide-react';

// 메인 대시보드 컴포넌트
export default function FraudDetectionDashboard() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // KPI 데이터
  const kpiData = {
    totalClaims: { value: 1250, change: 25, trend: 'up' },
    fraudDetected: { value: 45, change: 2, trend: 'up' },
    pendingReview: { value: 12, change: -5, trend: 'down' },
    potentialSavings: { value: 450000, change: 15000, trend: 'up' }
  };

  // Risk Distribution 데이터
  const riskDistribution = [
    { name: 'Low', value: 72, color: '#10B981' },
    { name: 'Medium', value: 20, color: '#FBBF24' },
    { name: 'High', value: 6.4, color: '#F97316' },
    { name: 'Critical', value: 1.6, color: '#EF4444' }
  ];

  // Agent Contribution 데이터
  const agentContribution = [
    { name: 'Statistical', rate: 15, color: '#3B82F6', icon: '📊' },
    { name: 'ML Pattern', rate: 25, color: '#60A5FA', icon: '🤖' },
    { name: 'Rule Compliance', rate: 40, color: '#EF4444', icon: '📋' },
    { name: 'Feature Store', rate: 8, color: '#FCA5A5', icon: '🗄️' },
    { name: 'Graph', rate: 12, color: '#14B8A6', icon: '🔗' }
  ];

  // 실시간 분석 데이터
  const realtimeData = [
    { time: '09:00', claims: 45, fraud: 2 },
    { time: '10:00', claims: 62, fraud: 3 },
    { time: '11:00', claims: 78, fraud: 5 },
    { time: '12:00', claims: 55, fraud: 2 },
    { time: '13:00', claims: 89, fraud: 4 },
    { time: '14:00', claims: 95, fraud: 6 },
    { time: '15:00', claims: 82, fraud: 3 },
    { time: 'Now', claims: 73, fraud: 4 }
  ];

  // 최근 분석된 청구 목록
  const recentClaims = [
    { id: 'CLM-2024-001', provider: 'PRV001', amount: 9500, risk: 'critical', score: 0.92, status: 'flagged' },
    { id: 'CLM-2024-002', provider: 'PRV045', amount: 450, risk: 'low', score: 0.15, status: 'approved' },
    { id: 'CLM-2024-003', provider: 'PRV002', amount: 2300, risk: 'high', score: 0.78, status: 'review' },
    { id: 'CLM-2024-004', provider: 'PRV078', amount: 180, risk: 'low', score: 0.08, status: 'approved' },
    { id: 'CLM-2024-005', provider: 'PRV003', amount: 5600, risk: 'medium', score: 0.45, status: 'review' }
  ];

  // Agent 상세 정보
  const agentDetails = [
    { name: 'Statistical Agent', status: 'online', latency: '12ms', accuracy: '94.2%' },
    { name: 'ML Pattern Agent', status: 'online', latency: '45ms', accuracy: '97.8%' },
    { name: 'Rule Compliance Agent', status: 'online', latency: '8ms', accuracy: '99.9%' },
    { name: 'Feature Store Agent', status: 'online', latency: '23ms', accuracy: '96.1%' },
    { name: 'Knowledge Graph Agent', status: 'online', latency: '67ms', accuracy: '91.5%' }
  ];

  const getRiskColor = (risk) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800'
    };
    return colors[risk] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'flagged': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'review': return <Clock className="w-4 h-4 text-yellow-500" />;
      default: return null;
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  };

  // 시뮬레이션: 새 청구 분석
  const simulateAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* 사이드바 */}
      <div className="w-64 bg-white border-r border-gray-200 p-4">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-gray-900">Fraud Detection</h1>
            <p className="text-xs text-gray-500">Compound AI System</p>
          </div>
        </div>

        <nav className="space-y-1">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Navigation</p>
          {[
            { id: 'dashboard', label: 'Dashboard', icon: Activity },
            { id: 'realtime', label: 'Real-time Analysis', icon: Zap },
            { id: 'agents', label: 'Agent Status', icon: Brain },
            { id: 'reports', label: 'Reports', icon: FileText }
          ].map(item => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${activeNav === item.id
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="mt-8 p-4 bg-green-50 rounded-xl border border-green-200">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium text-green-800">System Online</span>
          </div>
          <p className="text-xs text-green-600">5 Agents Active</p>
          <p className="text-xs text-green-600">Avg Latency: 31ms</p>
        </div>

        {/* Agent 미니 상태 */}
        <div className="mt-4 space-y-2">
          <p className="text-xs font-semibold text-gray-400 uppercase">Active Agents</p>
          {['Statistical', 'ML Pattern', 'Rule', 'Feature', 'Graph'].map((agent, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-gray-600">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
              {agent}
            </div>
          ))}
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex-1 p-6 overflow-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              📊 Fraud Detection Dashboard
            </h2>
            <p className="text-sm text-gray-500 mt-1">Real-time monitoring powered by Compound AI</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={simulateAnalysis}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Analyze New Claim
                </>
              )}
            </button>
            <button className="p-2 text-gray-400 hover:text-gray-600 relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">3</span>
            </button>
          </div>
        </div>

        {/* KPI 카드 */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            { title: 'Total Claims Analyzed', value: kpiData.totalClaims.value.toLocaleString(), change: `+${kpiData.totalClaims.change} today`, trend: 'up', icon: FileText, color: 'blue' },
            { title: 'Fraud Detected', value: kpiData.fraudDetected.value, change: `+${kpiData.fraudDetected.change} today`, trend: 'up', icon: AlertTriangle, color: 'red' },
            { title: 'Pending Review', value: kpiData.pendingReview.value, change: `${kpiData.pendingReview.change}`, trend: 'down', icon: Clock, color: 'yellow' },
            { title: 'Potential Savings', value: formatCurrency(kpiData.potentialSavings.value), change: `+${formatCurrency(kpiData.potentialSavings.change)}`, trend: 'up', icon: DollarSign, color: 'green' }
          ].map((kpi, index) => (
            <div key={index} className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-gray-500">{kpi.title}</span>
                <kpi.icon className={`w-5 h-5 text-${kpi.color}-500`} />
              </div>
              <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
              <p className={`text-sm mt-1 flex items-center gap-1 ${kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {kpi.trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                {kpi.change}
              </p>
            </div>
          ))}
        </div>

        {/* 차트 영역 */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Risk Distribution */}
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">Risk Distribution</h3>
            <div className="flex items-center">
              <div className="w-1/2">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {riskDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-1/2 space-y-3">
                {riskDistribution.map((item, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-sm text-gray-600 flex-1">{item.name}</span>
                    <span className="text-sm font-medium text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Agent Contribution */}
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">Agent Contribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={agentContribution} layout="horizontal">
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(value) => [`${value}%`, 'Detection Rate']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
                  {agentContribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 실시간 트렌드 & 최근 청구 */}
        <div className="grid grid-cols-3 gap-6">
          {/* 실시간 트렌드 */}
          <div className="col-span-2 bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">Real-time Analysis Trend</h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={realtimeData}>
                <defs>
                  <linearGradient id="colorClaims" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                <Area type="monotone" dataKey="claims" stroke="#3B82F6" fillOpacity={1} fill="url(#colorClaims)" name="Claims" />
                <Area type="monotone" dataKey="fraud" stroke="#EF4444" fillOpacity={1} fill="url(#colorFraud)" name="Fraud" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* 최근 분석 청구 */}
          <div className="bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
            <h3 className="font-semibold text-gray-900 mb-4">Recent Claims</h3>
            <div className="space-y-3">
              {recentClaims.map((claim, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                  onClick={() => setSelectedClaim(claim)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">{claim.id}</span>
                    {getStatusIcon(claim.status)}
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{formatCurrency(claim.amount)}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getRiskColor(claim.risk)}`}>
                      {claim.risk.toUpperCase()}
                    </span>
                  </div>
                  <div className="mt-1">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${claim.score > 0.8 ? 'bg-red-500' :
                            claim.score > 0.5 ? 'bg-orange-500' :
                              claim.score > 0.3 ? 'bg-yellow-500' : 'bg-green-500'
                          }`}
                        style={{ width: `${claim.score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Agent 상태 테이블 */}
        <div className="mt-6 bg-white rounded-xl p-5 border border-gray-200 shadow-sm">
          <h3 className="font-semibold text-gray-900 mb-4">Agent Performance Monitor</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="pb-3">Agent</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Latency</th>
                  <th className="pb-3">Accuracy</th>
                  <th className="pb-3">Last Active</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {agentDetails.map((agent, index) => (
                  <tr key={index} className="text-sm">
                    <td className="py-3 font-medium text-gray-900">{agent.name}</td>
                    <td className="py-3">
                      <span className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-green-600">Online</span>
                      </span>
                    </td>
                    <td className="py-3 text-gray-600">{agent.latency}</td>
                    <td className="py-3">
                      <span className="text-green-600 font-medium">{agent.accuracy}</span>
                    </td>
                    <td className="py-3 text-gray-500">Just now</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 선택된 청구 상세 모달 */}
        {selectedClaim && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setSelectedClaim(null)}>
            <div className="bg-white rounded-2xl p-6 w-full max-w-lg mx-4" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">Claim Analysis Detail</h3>
                <button onClick={() => setSelectedClaim(null)} className="text-gray-400 hover:text-gray-600">✕</button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500">Claim ID</p>
                    <p className="font-medium">{selectedClaim.id}</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500">Provider</p>
                    <p className="font-medium">{selectedClaim.provider}</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500">Amount</p>
                    <p className="font-medium">{formatCurrency(selectedClaim.amount)}</p>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500">Risk Score</p>
                    <p className="font-bold text-lg">{(selectedClaim.score * 100).toFixed(0)}%</p>
                  </div>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Agent Analysis Results</p>
                  <div className="space-y-2">
                    {[
                      { name: 'Statistical', score: 0.65, finding: 'Z-score 16.0 - 극단적 이상치' },
                      { name: 'ML Pattern', score: 0.90, finding: '사기 패턴과 92% 유사' },
                      { name: 'Rule Compliance', score: 0.90, finding: 'CMS 상한 초과' },
                      { name: 'Feature Store', score: 0.79, finding: '거부율 59%' },
                      { name: 'Knowledge Graph', score: 0.65, finding: '사기 링 연관' }
                    ].map((agent, i) => (
                      <div key={i} className="flex items-center gap-3 p-2 bg-gray-50 rounded">
                        <div className="w-24 text-xs font-medium">{agent.name}</div>
                        <div className="flex-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${agent.score > 0.7 ? 'bg-red-500' : agent.score > 0.4 ? 'bg-yellow-500' : 'bg-green-500'}`}
                              style={{ width: `${agent.score * 100}%` }}
                            />
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 w-36 truncate">{agent.finding}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-3">
                  <button className="flex-1 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
                    Approve
                  </button>
                  <button className="flex-1 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700">
                    Flag for Investigation
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
