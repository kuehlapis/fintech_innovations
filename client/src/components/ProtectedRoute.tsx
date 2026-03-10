import { Navigate } from "react-router-dom";
import { getAccessToken, getStoredUserId } from "@/lib/storage";

export default function ProtectedRoute({ children }: { children: JSX.Element }) {
  const userId = getStoredUserId();
  const token = getAccessToken();

  if (!userId || !token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
