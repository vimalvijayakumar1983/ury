import React, { useState, useEffect } from 'react';
import { useBranchContext } from '../../context/BranchContext';
import KPIGrid from './KPIGrid';
import AnalyticsCharts from './AnalyticsCharts';
import ReportWidgets from './ReportWidgets';
import {
  dashboardService,
  DashboardSummary,
  DashboardChartsData,
  TransactionRecord,
} from '../../services/dashboard';

export const DashboardPage: React.FC = () => {
  const { activeBranchId } = useBranchContext();

  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [chartsData, setChartsData] = useState<DashboardChartsData | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<TransactionRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [sumRes, chartRes, txRes] = await Promise.all([
        dashboardService.getSummary(activeBranchId),
        dashboardService.getCharts(activeBranchId),
        dashboardService.getRecentTransactions(activeBranchId, 10),
      ]);
      setSummary(sumRes);
      setChartsData(chartRes);
      setRecentTransactions(txRes);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [activeBranchId]);

  return (
    <div className="space-y-6">
      <nav aria-label="Restaurant workspace" className="flex flex-wrap items-center gap-3">
        <a href="/pos" className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground">
          Open cashier POS
        </a>
        <a href="/app/vav-recipe-cost-sheet" className="rounded-lg border px-4 py-2 text-sm font-semibold">
          Recipe cost sheets
        </a>
      </nav>

      <KPIGrid summary={summary} loading={loading} />

      {/* 2. Analytics & Distribution Charts (Commented out for now) */}
      {/* <AnalyticsCharts chartsData={chartsData} loading={loading} /> */}

      {/* 3. Live Recent Transactions */}
      <ReportWidgets recentTransactions={recentTransactions} loading={loading} />
    </div>
  );
};

export default DashboardPage;
