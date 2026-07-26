import React, { useState } from 'react';
import { ShieldCheck, ArrowRight } from 'lucide-react';

export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      await onLogin(username, password);
    } catch (err) {
      setError(err.message || 'Sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={23}/>
          </div>
          <span>SENTINEL</span>
        </div>
        <div className="login-copy">
          <span>SECURE COMMAND ACCESS</span>
          <h1>Sign in to Sentinel</h1>
          <p>Use your agency-issued account. Access is logged and restricted by role.</p>
        </div>
        <form onSubmit={submit}>
          <label>
            Username
            <input 
              value={username} 
              onChange={event => setUsername(event.target.value)} 
              autoComplete="username" 
              required 
            />
          </label>
          <label>
            Password
            <input 
              type="password" 
              value={password} 
              onChange={event => setPassword(event.target.value)} 
              autoComplete="current-password" 
              required 
            />
          </label>
          {error && <p className="login-error">{error}</p>}
          <button className="primary-button login-submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Secure sign in'} <ArrowRight size={17}/>
          </button>
        </form>
        <p className="login-notice">Authorised use only. Activity is retained in the audit log.</p>
      </section>
    </main>
  );
}
