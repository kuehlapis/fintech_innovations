import { useState } from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import { login } from "@/lib/api";
import { setAccessToken, setRefreshToken, setStoredUserId } from "@/lib/storage";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;

    setLoading(true);
    try {
      const res = await login(email.trim(), password);
      if (!res.user_id || !res.access_token) throw new Error("No token returned");
      setStoredUserId(res.user_id);
      setAccessToken(res.access_token);
      setRefreshToken(res.refresh_token ?? "");
      setMessage("Login successful.");
      navigate("/dashboard");
    } catch {
      setMessage("Login failed. Check your credentials or confirm your email.");
    } finally {
      setLoading(false);
    }
  };

  const handleGuest = () => {
    setStoredUserId("guest");
    navigate("/holdings");
  };

  return (
    <div className="max-w-md mx-auto space-y-8">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <h1 className="font-display text-3xl font-bold text-foreground">Log in</h1>
        <p className="mt-1 text-sm text-muted-foreground">Access your OneWealth account.</p>
      </motion.div>

      <motion.form
        onSubmit={handleSubmit}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5 }}
        className="rounded-xl border border-border bg-card p-6 space-y-4"
      >
        <label className="block">
          <span className="text-sm font-medium text-card-foreground">Email</span>
          <input
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="mt-2 w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm text-foreground"
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-card-foreground">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Your password"
            className="mt-2 w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm text-foreground"
          />
        </label>

        <button
          type="submit"
          disabled={!email.trim() || !password.trim() || loading}
          className="w-full rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Log in"}
        </button>

        <button
          type="button"
          onClick={handleGuest}
          className="w-full rounded-lg border border-border bg-muted px-4 py-2.5 text-sm font-semibold text-foreground"
        >
          Continue as guest
        </button>

        {message && <p className="text-sm text-muted-foreground">{message}</p>}

        <p className="text-sm text-muted-foreground">
          New to OneWealth? <Link className="text-primary hover:underline" to="/signup">Create an account</Link>
        </p>
      </motion.form>
    </div>
  );
}
