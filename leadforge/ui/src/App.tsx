import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppLayout } from "./layouts/AppLayout";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { CampaignWizard } from "./pages/CampaignWizard";
import { ReviewQueue } from "./pages/ReviewQueue";
import { Analytics } from "./pages/Analytics";
import { Clients } from "./pages/Clients";
import { Settings } from "./pages/Settings";

const queryClient = new QueryClient();

function RequireAuth({ children }: { children: React.ReactNode }) {
  return localStorage.getItem("access_token") ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <AppLayout />
              </RequireAuth>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="campaigns/new" element={<CampaignWizard />} />
            <Route path="review" element={<ReviewQueue />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="clients" element={<Clients />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
