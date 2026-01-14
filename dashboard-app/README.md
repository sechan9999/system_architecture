# Healthcare Fraud Detection Dashboard

A modern, responsive React dashboard for visualizing and monitoring healthcare fraud detection in real-time. Built with Vite, React 19, and Tailwind CSS v4.

## 🎯 Features

### Real-time Monitoring
- **Live KPI Tracking** - Total claims, fraud detection rate, pending reviews, and potential savings
- **Real-time Analytics** - Hourly claim processing and fraud detection trends
- **Risk Distribution** - Visual breakdown of claims by risk level (Low, Medium, High, Critical)

### Agent Performance
- **Multi-Agent Contribution** - Track performance of 5 specialized AI agents:
  - 📊 Statistical Anomaly Agent
  - 🤖 ML Pattern Agent
  - 📋 Rule Compliance Agent
  - 🗄️ Feature Store Agent
  - 🔗 Knowledge Graph Agent

### Interactive Analysis
- **Claim Investigation** - Detailed view of individual claims with risk scoring
- **Agent Insights** - See which agents flagged each issue and why
- **Historical Trends** - Weekly detection trends and patterns

## 🚀 Quick Start

### Prerequisites
- Node.js 20+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development
The app will be available at `http://localhost:5173`

## 📦 Technology Stack

- **React 19.2** - Latest React with improved hooks and performance
- **Vite 7.2** - Lightning-fast build tool with HMR
- **Tailwind CSS 4.1** - Utility-first CSS framework
- **Recharts 3.6** - Composable charting library
- **Framer Motion 12** - Production-ready motion library
- **Lucide React** - Beautiful, consistent icon set

## 🏗️ Project Structure

```
dashboard-app/
├── src/
│   ├── App.jsx           # Main dashboard component
│   ├── main.jsx          # React entry point
│   ├── mockLogic.js      # Mock fraud detection logic
│   ├── App.css           # Component styles
│   └── index.css         # Global styles & Tailwind imports
├── public/               # Static assets
├── index.html            # HTML entry point
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
└── package.json          # Dependencies and scripts
```

## 🎨 Dashboard Sections

### 1. Overview Dashboard
- **KPI Cards** - Key metrics with trend indicators
- **Risk Distribution Chart** - Pie chart showing claim risk levels
- **Agent Performance** - Bar chart of agent detection rates
- **Real-time Activity** - Line chart of hourly processing

### 2. Recent Claims
- Sortable table of analyzed claims
- Risk level indicators
- Quick access to detailed analysis

### 3. Claim Details
- Comprehensive risk assessment
- Agent-by-agent findings
- Patient and provider information
- Recommended actions

## 🔧 Configuration

### GitHub Pages Deployment

The dashboard is configured for GitHub Pages deployment:

```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  base: "/system_architecture/",
})
```

**Important:** Update the `base` path if your repository name differs.

### Tailwind CSS

Tailwind is configured to scan all JSX/TSX files:

```javascript
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // ...
}
```

## 📊 Mock Data

The dashboard uses mock data for demonstration purposes (`mockLogic.js`). In production, connect to the backend API:

**Backend API:** See [../extracted/compound_ai_system/README.md](../extracted/compound_ai_system/README.md)

### Example API Integration

```javascript
// Replace mock data with real API calls
const analyzeClaim = async (claimData) => {
  const response = await fetch('http://your-api-url/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(claimData)
  });
  return await response.json();
};
```

## 🎭 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

## 🌐 Deployment

### GitHub Pages (Automated)

The dashboard deploys automatically via GitHub Actions on pushes to `main`:

1. Build runs on every push to `main`
2. Static files are generated in `dist/`
3. Deployed to GitHub Pages

See [../.github/workflows/deploy.yml](../.github/workflows/deploy.yml) for workflow details.

### Manual Deployment

```bash
# Build the project
npm run build

# Deploy the dist/ folder to your hosting service
# Examples: Netlify, Vercel, AWS S3, etc.
```

## 🔍 Key Components

### Dashboard Metrics
- Total claims processed
- Fraud detection rate
- Pending reviews
- Estimated cost savings

### Risk Levels
- 🟢 **Low** - Routine claims, minimal risk
- 🟡 **Medium** - Requires attention, minor anomalies
- 🟠 **High** - Suspicious patterns detected
- 🔴 **Critical** - High probability of fraud

### Agent Detection Types
- **Statistical Anomalies** - Z-scores, Benford's Law violations
- **ML Patterns** - Unusual patterns from Isolation Forest
- **Rule Violations** - CMS compliance issues
- **Feature Anomalies** - Historical pattern deviations
- **Network Flags** - Suspicious provider relationships

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1024px - 1920px)
- Tablet (768px - 1024px)
- Mobile (< 768px)

## 🤝 Contributing

1. Follow the existing code style
2. Use Tailwind CSS for styling (avoid custom CSS when possible)
3. Test on multiple screen sizes
4. Update this README for new features

## 📄 License

MIT License - see [../README.md](../README.md) for details

## 🔗 Related Documentation

- [Backend System Documentation](../extracted/compound_ai_system/README.md)
- [Root Project README](../README.md)
- [Vite Documentation](https://vite.dev)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com)
