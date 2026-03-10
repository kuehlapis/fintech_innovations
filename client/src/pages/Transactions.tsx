import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createAccount, createTransaction, getAccounts } from "@/lib/api";
import { getStoredUserId } from "@/lib/storage";

export default function Transactions() {
  const userId = getStoredUserId();
  const queryClient = useQueryClient();

  const [accountName, setAccountName] = useState("");
  const [accountType, setAccountType] = useState<"bank" | "credit_card">("bank");
  const [institution, setInstitution] = useState("");

  const [selectedAccount, setSelectedAccount] = useState("");
  const [txDate, setTxDate] = useState(new Date().toISOString().slice(0, 10));
  const [txType, setTxType] = useState<"income" | "expense" | "transfer">("expense");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [message, setMessage] = useState("");

  const accountsQuery = useQuery({
    queryKey: ["accounts", userId],
    queryFn: () => getAccounts(userId),
    enabled: Boolean(userId && userId !== "guest"),
  });

  const accounts = useMemo(() => accountsQuery.data?.accounts ?? [], [accountsQuery.data]);

  const createAccountMutation = useMutation({
    mutationFn: () =>
      createAccount({
        user_id: userId,
        account_name: accountName,
        account_type: accountType,
        institution_name: institution,
      }),
    onSuccess: () => {
      setMessage("Account created.");
      setAccountName("");
      setInstitution("");
      queryClient.invalidateQueries({ queryKey: ["accounts", userId] });
    },
    onError: () => setMessage("Unable to create account."),
  });

  const createTransactionMutation = useMutation({
    mutationFn: () =>
      createTransaction({
        account_id: selectedAccount,
        transaction_date: txDate,
        transaction_type: txType,
        amount: Number(amount),
        category,
        description,
      }),
    onSuccess: () => {
      setMessage("Transaction saved and analysis triggered.");
      setAmount("");
      setCategory("");
      setDescription("");
    },
    onError: () => setMessage("Unable to create transaction."),
  });

  if (!userId || userId === "guest") {
    return <div className="rounded-xl border border-border bg-card p-4 text-sm text-muted-foreground">Please log in to manage transactions.</div>;
  }

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <h2 className="font-display text-lg font-semibold">Create Financial Account</h2>
        <div className="grid gap-3 md:grid-cols-4">
          <input value={accountName} onChange={(e) => setAccountName(e.target.value)} placeholder="Account name" className="rounded-lg border px-3 py-2 text-sm" />
          <input value={institution} onChange={(e) => setInstitution(e.target.value)} placeholder="Institution" className="rounded-lg border px-3 py-2 text-sm" />
          <select value={accountType} onChange={(e) => setAccountType(e.target.value as "bank" | "credit_card")} className="rounded-lg border px-3 py-2 text-sm">
            <option value="bank">Bank</option>
            <option value="credit_card">Credit Card</option>
          </select>
          <button
            onClick={() => createAccountMutation.mutate()}
            disabled={!accountName.trim() || createAccountMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
          >
            {createAccountMutation.isPending ? "Creating..." : "Create Account"}
          </button>
        </div>
      </section>

      <section className="rounded-xl border border-border bg-card p-6 space-y-4">
        <h2 className="font-display text-lg font-semibold">Add Transaction</h2>
        <div className="grid gap-3 md:grid-cols-3">
          <select value={selectedAccount} onChange={(e) => setSelectedAccount(e.target.value)} className="rounded-lg border px-3 py-2 text-sm">
            <option value="">Select account</option>
            {accounts.map((a) => (
              <option key={a.id} value={a.id}>{a.account_name}</option>
            ))}
          </select>
          <input type="date" value={txDate} onChange={(e) => setTxDate(e.target.value)} className="rounded-lg border px-3 py-2 text-sm" />
          <select value={txType} onChange={(e) => setTxType(e.target.value as "income" | "expense" | "transfer")} className="rounded-lg border px-3 py-2 text-sm">
            <option value="income">Income</option>
            <option value="expense">Expense</option>
            <option value="transfer">Transfer</option>
          </select>
          <input value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="Amount" type="number" className="rounded-lg border px-3 py-2 text-sm" />
          <input value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Category" className="rounded-lg border px-3 py-2 text-sm" />
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" className="rounded-lg border px-3 py-2 text-sm" />
        </div>
        <button
          onClick={() => createTransactionMutation.mutate()}
          disabled={!selectedAccount || !amount || createTransactionMutation.isPending}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground disabled:opacity-50"
        >
          {createTransactionMutation.isPending ? "Saving..." : "Save Transaction"}
        </button>
      </section>

      {message && <p className="text-sm text-muted-foreground">{message}</p>}
    </div>
  );
}