import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Login } from "./pages/Login";
import { ReviewQueue } from "./pages/ReviewQueue";

const queryClient = new QueryClient();

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("access_token"));

  if (!isLoggedIn) {
    return <Login onLogin={() => setIsLoggedIn(true)} />;
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b px-6 py-3 flex justify-between items-center">
          <h1 className="font-bold text-gray-900">LeadForge</h1>
          <button onClick={() => { localStorage.removeItem("access_token"); setIsLoggedIn(false); }}
            className="text-sm text-gray-500 hover:text-gray-700">Sign out</button>
        </nav>
        <ReviewQueue />
      </div>
    </QueryClientProvider>
  );
}
