
// Mock Agent Logic (ported from Python)
export const analyzeClaim = async (claim) => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    const results = [];
    const checks = [];

    // 1. Statistical Anomaly Agent
    let statScore = 0.1;
    const statFindings = [];

    // Z-score logic via Benford's law simulation
    const firstDigit = parseInt(String(claim.amount)[0]);
    if (firstDigit === 9) {
        statScore += 0.4;
        statFindings.push("Benford's Law violation (Leading digit 9)");
    }

    if (claim.amount > 5000) {
        statScore += 0.5;
        statFindings.push(`Extreme outlier amount for ${claim.specialty} (Z-Score > 3)`);
    }

    results.push({
        name: "Statistical Anomaly Agent",
        risk: Math.min(statScore, 1.0),
        confidence: 0.85,
        findings: statFindings.length > 0 ? statFindings : ["No statistical anomalies detected"]
    });

    // 2. Rule Compliance Agent
    let ruleScore = 0.05;
    const ruleFindings = [];

    if (["PRV999", "PRV888"].includes(claim.providerId)) {
        ruleScore = 1.0;
        ruleFindings.push("Provider is on Sanctions List");
    }

    if (claim.amount > 8000) { // Simple CMS limit rule
        ruleScore = Math.max(ruleScore, 0.9);
        ruleFindings.push("Exceeds CMS max allowable for procedure");
    }

    results.push({
        name: "Rule Compliance Agent",
        risk: Math.min(ruleScore, 1.0),
        confidence: 0.95,
        findings: ruleFindings.length > 0 ? ruleFindings : ["Compliant with all CMS rules"]
    });

    // 3. ML Pattern Agent
    let mlScore = 0.2;
    const mlFindings = [];

    // Suspicious procedure-diagnosis combo
    if (claim.procedureCode === "93306" && claim.diagnosisCode.startsWith("M54")) {
        mlScore += 0.6;
        mlFindings.push("Rare Procedure-Diagnosis pair (0.01% freq)");
    }

    if (claim.age < 30 && claim.specialty === "Cardiology") {
        mlScore += 0.3;
        mlFindings.push("Unusual Age group for Cardiology procedures");
    }

    results.push({
        name: "ML Pattern Agent",
        risk: Math.min(mlScore, 1.0),
        confidence: 0.75,
        findings: mlFindings.length > 0 ? mlFindings : ["Consistent with historical patterns"]
    });

    // 4. Knowledge Graph Agent
    let graphScore = 0.15;
    const graphFindings = [];

    if (claim.providerId === "PRV001") {
        graphScore = 0.65;
        graphFindings.push("Connected to known fraud ring #442");
        graphFindings.push("High centrality in suspicious referral network");
    }

    results.push({
        name: "Knowledge Graph Agent",
        risk: Math.min(graphScore, 1.0),
        confidence: 0.80,
        findings: graphFindings.length > 0 ? graphFindings : ["No suspicious network connections"]
    });

    // 5. Feature Store Agent
    results.push({
        name: "Feature Store Agent",
        risk: 0.3,
        confidence: 0.6,
        findings: ["Provider velocity normal (15 claims/day)", "Beneficiary history clean"]
    });

    // Orchestration (Weighted Average)
    const totalWeight = results.reduce((sum, r) => sum + r.confidence, 0);
    const weightedRisk = results.reduce((sum, r) => sum + (r.risk * r.confidence), 0) / totalWeight;

    let riskLevel = "low";
    let action = "AUTO_APPROVE";

    if (weightedRisk > 0.7) {
        riskLevel = "critical";
        action = "AUTO_DENY";
    } else if (weightedRisk > 0.5) {
        riskLevel = "high";
        action = "FLAG_FOR_INVESTIGATION";
    } else if (weightedRisk > 0.3) {
        riskLevel = "medium";
        action = "MANUAL_REVIEW";
    }

    return {
        riskLevel,
        score: weightedRisk,
        action,
        explanation: `Weighted risk score of ${weightedRisk.toFixed(3)} indicates ${riskLevel.toUpperCase()} risk. Primary drivers: ${results.filter(r => r.risk > 0.5).map(r => r.name).join(", ") || "None"}.`,
        keyFindings: results.flatMap(r => r.findings).filter(f => !f.includes("No ")).slice(0, 4),
        agentResults: results
    };
};

export const MOCK_TEMPLATES = {
    "Normal Claim": {
        claimId: "CLM001", providerId: "PRV010", beneficiaryId: "BEN001",
        procedureCode: "99213", diagnosisCode: "J06.9", amount: 120.0,
        specialty: "General Practice", age: 45
    },
    "Suspicious (High Amount)": {
        claimId: "CLM002", providerId: "PRV001", beneficiaryId: "BEN002",
        procedureCode: "93306", diagnosisCode: "M54.5", amount: 8500.0,
        specialty: "Cardiology", age: 28
    },
    "Fraud (Sanctioned Provider)": {
        claimId: "CLM003", providerId: "PRV999", beneficiaryId: "BEN003",
        procedureCode: "99215", diagnosisCode: "Z00.00", amount: 950.0,
        specialty: "General Practice", age: 70
    }
};
