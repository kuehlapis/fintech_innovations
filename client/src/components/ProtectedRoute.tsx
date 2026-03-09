import { Navigate } from "react-router-dom";
import { getStoredUserId } from "@/lib/storage";

export default function ProtectedRoute({ children }: { children: JSX.Element }) {
  const userId = getStoredUserId();

  if (!userId) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
