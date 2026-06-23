import { useEffect, useMemo, useState } from 'react';
import {
  Bell,
  CheckCircle2,
  Copy,
  CreditCard,
  Crown,
  LayoutDashboard,
  LineChart,
  Lock,
  LogOut,
  Package,
  Search,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  UserCircle2,
  Zap,
} from 'lucide-react';

type Tier = 'free' | 'basic' | 'pro';
type View = 'command' | 'trends' | 'subscription';
type CopyType = 'blog' | 'script' | 'social';
type TrendView = 'public' | 'premium';

interface User {
  id: string;
  username: string;
  email: string;
  tier: Tier;
}

interface ApiProduct {
  id: string;
  name: string;
  description: string;
  category: string;
  estimated_price: number;
  image_url?: string;
}

interface TrendItem {
  id: string;
  product_id: string;
  velocity_score: number;
  purchase_intent_ratio: number;
  status: string;
  access_level: TrendView;
  locked: boolean;
  scanned_at: string;
  source_platform?: string;
  source_external_id?: string;
  source_url?: string;
  source_subreddit?: string;
  source_title?: string;
  source_author?: string;
  source_created_at?: string;
  source_collected_at?: string;
  source_ingest_method?: string;
  live_source_verified?: boolean;
  provenance?: Record<string, unknown>;
  product: ApiProduct;
}

interface SubscriptionPlan {
  id: string;
  name: string;
  price_monthly: number;
  description: string;
  features: string[];
  checkout_status: string;
}

interface SubscriptionOverview {
  current_tier: Tier;
  checkout_mode: string;
  message: string;
  plans: SubscriptionPlan[];
  notes: string[];
}

interface AdminData {
  revenue: {
    total: number;
    saas_mrr: number;
    affiliate: number;
    currency: string;
  };
  traffic: {
    daily: number;
    weekly: number;
    monthly: number;
    history: Array<{ date: string; subs?: number; visitors?: number }>;
  };
  trending_products_today: number;
  content_status: {
    published: number;
    scheduled: number;
  };
  top_performing_posts: Array<{ title: string; revenue: number; views: number }>;
  subscribers: {
    count: number;
    conversion_rate: string;
    history: Array<{ date: string; subs: number }>;
  };
  process_health: {
    saas_server: string;
    blog_server: string;
    scheduler_daemon: string;
  };
  alert_log: Array<{ id: string; timestamp: string; type: string; message: string }>;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

const STORAGE_KEY = 'trendcatcher.token';

const PRODUCT_NOTES: Record<string, { features: string[]; keywords: string[] }> = {
  'Smart Galaxy Nebula Projector': {
    features: [
      'App-controlled lighting presets',
      'Bedroom decor appeal with viral social proof',
      'High purchase-intent audience on TikTok and Pinterest',
    ],
    keywords: ['galaxy projector', 'room decor lighting', 'viral bedroom gadget'],
  },
  'Levitating Floating Bonsai Pot': {
    features: [
      'Visually surprising product demonstration',
      'Premium gift positioning for creators and desks',
      'Strong save/share behavior on Pinterest and Reddit',
    ],
    keywords: ['levitating bonsai', 'floating planter', 'viral home decor'],
  },
  'Sunset Atmosphere Projection Lamp': {
    features: [
      'Low-ticket impulse purchase',
      'Easy before/after transformation content',
      'Reliable aesthetic-room niche fit',
    ],
    keywords: ['sunset lamp', 'golden hour projector', 'aesthetic room light'],
  },
  'Retro Wooden Mechanical Keyboard': {
    features: [
      'Higher-ticket premium accessory',
      'Strong creator/workspace audience fit',
      'Visual ASMR-friendly demo potential',
    ],
    keywords: ['mechanical keyboard', 'desk setup accessory', 'retro keyboard'],
  },
  'Self-Heating Smart Mug': {
    features: [
      'Evergreen work-from-home utility angle',
      'Easy UGC demo around convenience',
      'Premium accessory suited for paid subscribers',
    ],
    keywords: ['smart mug', 'desk gadget', 'heated coffee mug'],
  },
};

const emptyAdminData: AdminData = {
  revenue: { total: 0, saas_mrr: 0, affiliate: 0, currency: 'USD' },
  traffic: { daily: 0, weekly: 0, monthly: 0, history: [] },
  trending_products_today: 0,
  content_status: { published: 0, scheduled: 0 },
  top_performing_posts: [],
  subscribers: { count: 0, conversion_rate: '0.0%', history: [] },
  process_health: { saas_server: 'green', blog_server: 'red', scheduler_daemon: 'red' },
  alert_log: [],
};

function formatCurrency(value: number) {
  return value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function buildDrafts(trend: TrendItem) {
  const notes = PRODUCT_NOTES[trend.product.name] ?? {
    features: ['Cross-platform creator interest', 'Strong visual demo format', 'Good affiliate monetization fit'],
    keywords: ['viral product', 'creator trend', 'affiliate product'],
  };

  return {
    features: notes.features,
    keywords: notes.keywords,
    blog: `## ${trend.product.name}: why creators are watching this trend\n\n${trend.product.description}\n\n### Why it stands out\n- Velocity score: ${trend.velocity_score.toFixed(1)}\n- Purchase intent ratio: ${(trend.purchase_intent_ratio * 100).toFixed(0)}%\n- Access level: ${trend.access_level}\n\n### Content angle\nPosition this as a ${trend.product.category.toLowerCase()} product with clear creator-friendly hooks and a fast visual payoff.`,
    script: `Hook: "This ${trend.product.category.toLowerCase()} product keeps showing up for a reason."\n\nBody: Show the product, call out the ${trend.velocity_score.toFixed(1)} velocity signal, and demonstrate the top creator benefit in under 10 seconds.\n\nCTA: Invite viewers to check the product breakdown and comparison link.`,
    social: `Creators are already testing ${trend.product.name}. Velocity is ${trend.velocity_score.toFixed(1)} and purchase intent is ${(trend.purchase_intent_ratio * 100).toFixed(0)}%. Save this for your next affiliate content sprint.`,
  };
}

function tierBadgeColor(tier: Tier) {
  if (tier === 'pro') return 'bg-amber-500/15 text-amber-300 border-amber-500/30';
  if (tier === 'basic') return 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30';
  return 'bg-slate-800 text-slate-300 border-slate-700';
}

export default function App() {
  const [token, setToken] = useState<string>(() => localStorage.getItem(STORAGE_KEY) ?? '');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [view, setView] = useState<View>('trends');
  const [trendView, setTrendView] = useState<TrendView>('public');
  const [copyType, setCopyType] = useState<CopyType>('blog');
  const [selectedTrendId, setSelectedTrendId] = useState<string>('');
  const [trends, setTrends] = useState<TrendItem[]>([]);
  const [adminData, setAdminData] = useState<AdminData>(emptyAdminData);
  const [subscriptionData, setSubscriptionData] = useState<SubscriptionOverview | null>(null);
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [toast, setToast] = useState<{ visible: boolean; message: string }>({ visible: false, message: '' });

  const pushToast = (message: string) => {
    setToast({ visible: true, message });
    window.setTimeout(() => setToast({ visible: false, message: '' }), 2800);
  };

  const apiFetch = async <T,>(path: string, init?: RequestInit, includeAuth = true): Promise<T> => {
    const headers = new Headers(init?.headers ?? {});
    if (includeAuth && token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    if (init?.body && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    const response = await fetch(path, { ...init, headers });
    if (response.status === 401 && includeAuth) {
      localStorage.removeItem(STORAGE_KEY);
      setToken('');
      setCurrentUser(null);
    }
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || 'Request failed');
    }
    return response.json() as Promise<T>;
  };

  useEffect(() => {
    if (!token) {
      setCurrentUser(null);
      return;
    }

    apiFetch<User>('/api/auth/me')
      .then(setCurrentUser)
      .catch(() => {
        localStorage.removeItem(STORAGE_KEY);
        setToken('');
      });
  }, [token]);

  useEffect(() => {
    apiFetch<TrendItem[]>('/api/trends?include_locked=true', undefined, Boolean(token))
      .then(setTrends)
      .catch(() => setTrends([]));

    apiFetch<AdminData>('/api/admin/dashboard', undefined, false)
      .then(setAdminData)
      .catch(() => setAdminData(emptyAdminData));

    apiFetch<SubscriptionOverview>('/api/subscription/plans', undefined, Boolean(token))
      .then(setSubscriptionData)
      .catch(() => setSubscriptionData(null));
  }, [token, currentUser?.tier]);

  const paidAccess = currentUser?.tier === 'basic' || currentUser?.tier === 'pro';

  const visibleTrends = useMemo(() => {
    if (trendView === 'public') {
      return trends.filter((trend) => trend.access_level === 'public');
    }
    return trends.filter((trend) => trend.access_level === 'premium');
  }, [trendView, trends]);

  useEffect(() => {
    if (!visibleTrends.length) {
      setSelectedTrendId('');
      return;
    }
    if (!visibleTrends.some((trend) => trend.id === selectedTrendId)) {
      setSelectedTrendId(visibleTrends[0].id);
    }
  }, [visibleTrends, selectedTrendId]);

  const selectedTrend = useMemo(
    () => visibleTrends.find((trend) => trend.id === selectedTrendId) ?? visibleTrends[0] ?? null,
    [visibleTrends, selectedTrendId],
  );

  const selectedDrafts = selectedTrend ? buildDrafts(selectedTrend) : null;
  const hiddenPremiumCount = trends.filter((trend) => trend.access_level === 'premium').length;

  const handleAuth = async (event: React.FormEvent) => {
    event.preventDefault();
    setAuthLoading(true);
    setAuthError('');

    try {
      const endpoint = authMode === 'signup' ? '/api/auth/register' : '/api/auth/login';
      const payload = authMode === 'signup' ? { username, email, password } : { email, password };
      const response = await apiFetch<AuthResponse>(endpoint, {
        method: 'POST',
        body: JSON.stringify(payload),
      }, false);
      localStorage.setItem(STORAGE_KEY, response.access_token);
      setToken(response.access_token);
      setCurrentUser(response.user);
      setPassword('');
      pushToast(authMode === 'signup' ? 'Account created.' : 'Signed in successfully.');
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Authentication failed');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setToken('');
    setCurrentUser(null);
    setView('trends');
    setTrendView('public');
    pushToast('Signed out.');
  };

  const handleCopyDraft = async () => {
    if (!selectedTrend || !selectedDrafts) return;
    if (selectedTrend.locked) {
      pushToast('Upgrade to Basic or Pro to access premium trend content.');
      return;
    }
    await navigator.clipboard.writeText(selectedDrafts[copyType]);
    pushToast('Draft copied to clipboard.');
  };

  const renderHealthPill = (label: string, status: string) => (
    <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
      <div>
        <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">{label}</p>
        <p className="text-sm font-semibold text-slate-200 mt-1">{status === 'green' ? 'Active' : status === 'yellow' ? 'Degraded' : 'Offline'}</p>
      </div>
      <span className={`w-3 h-3 rounded-full ${status === 'green' ? 'bg-emerald-500' : status === 'yellow' ? 'bg-yellow-500' : 'bg-rose-500'}`}></span>
    </div>
  );

  const renderAuthShell = () => {
    const publicPreview = trends.filter((trend) => trend.access_level === 'public').slice(0, 3);

    return (
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <section className="xl:col-span-2 bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl">
          <div className="flex items-center gap-2 text-indigo-300 mb-4">
            <UserCircle2 className="w-5 h-5" />
            <span className="font-semibold">Account access</span>
          </div>
          <h1 className="text-3xl font-bold text-white">Sign in to save your tiered dashboard</h1>
          <p className="text-sm text-slate-400 mt-3 leading-relaxed">
            Create a free account to unlock the public trend feed. Basic and Pro tiers expose premium trend results once the lead wires live checkout links.
          </p>

          <form onSubmit={handleAuth} className="space-y-4 mt-6">
            {authMode === 'signup' && (
              <div>
                <label className="text-xs font-semibold text-slate-400 block mb-1.5">Username</label>
                <input
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-500"
                  placeholder="Creator dashboard name"
                />
              </div>
            )}
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Email</label>
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                required
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-500"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1.5">Password</label>
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                required
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 outline-none focus:border-indigo-500"
                placeholder="••••••••"
              />
            </div>
            {authError && <p className="text-sm text-rose-400">{authError}</p>}
            <button
              type="submit"
              disabled={authLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition"
            >
              {authLoading ? 'Working…' : authMode === 'signup' ? 'Create free account' : 'Sign in'}
            </button>
          </form>

          <button
            onClick={() => {
              setAuthMode(authMode === 'signup' ? 'login' : 'signup');
              setAuthError('');
            }}
            className="text-sm text-indigo-300 hover:text-indigo-200 mt-4"
          >
            {authMode === 'signup' ? 'Already have an account? Sign in.' : 'Need an account? Create one.'}
          </button>
        </section>

        <section className="xl:col-span-3 bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-5">
            <div>
              <p className="text-[11px] uppercase tracking-wider text-slate-500 font-bold">Public feed preview</p>
              <h2 className="text-2xl font-bold text-white mt-1">{publicPreview.length ? 'Verified Reddit trend feed' : 'No verified live trend feed yet'}</h2>
              <p className="text-sm text-slate-400 mt-2">
                {publicPreview.length
                  ? 'TrendCatcher is showing only rows fetched from Reddit public JSON with stored source provenance. Seeded and simulated trend records remain withheld.'
                  : 'TrendCatcher is live, but the public preview stays empty until Reddit public JSON ingestion writes verified provenance rows. Seeded and simulated trend records are withheld instead of being shown as live.'}
              </p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300">
              {hiddenPremiumCount} premium trends hidden
            </div>
          </div>

          <div className="space-y-3">
            {publicPreview.length === 0 ? (
              <div className="border border-dashed border-slate-700 rounded-xl p-6 text-sm text-slate-400 leading-relaxed">
                No verified live trends are available yet. The public preview will stay empty until Reddit public JSON ingestion writes rows with source provenance.
              </div>
            ) : publicPreview.map((trend) => (
              <div key={trend.id} className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex items-center justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-white">{trend.product.name}</h3>
                  <p className="text-sm text-slate-400">{trend.product.category} • Source: {trend.source_subreddit ? `r/${trend.source_subreddit}` : 'Reddit public JSON'}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 text-right text-sm">
                  <div>
                    <p className="text-slate-500">Velocity</p>
                    <p className="font-semibold text-indigo-300">{trend.velocity_score.toFixed(1)}</p>
                  </div>
                  <div>
                    <p className="text-slate-500">PIR</p>
                    <p className="font-semibold text-emerald-300">{(trend.purchase_intent_ratio * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    );
  };

  const renderCommandView = () => (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2"><LayoutDashboard className="w-6 h-6 text-indigo-400" /> Command dashboard</h1>
          <p className="text-sm text-slate-400 mt-2">Honest baseline reporting only. Unverified live metrics remain at zero until a verified source is wired.</p>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300">
          Logged in tier: <span className="font-semibold text-white">{currentUser?.tier ?? 'free'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {renderHealthPill('SaaS server', adminData.process_health.saas_server)}
        {renderHealthPill('Blog server', adminData.process_health.blog_server)}
        {renderHealthPill('Scheduler daemon', adminData.process_health.scheduler_daemon)}
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Total revenue</p>
          <p className="text-2xl font-bold text-white mt-2">${formatCurrency(adminData.revenue.total)}</p>
          <p className="text-xs text-slate-500 mt-1">Live baseline</p>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">SaaS MRR</p>
          <p className="text-2xl font-bold text-white mt-2">${formatCurrency(adminData.revenue.saas_mrr)}</p>
          <p className="text-xs text-slate-500 mt-1">Current confirmed sales</p>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Affiliate revenue</p>
          <p className="text-2xl font-bold text-white mt-2">${formatCurrency(adminData.revenue.affiliate)}</p>
          <p className="text-xs text-slate-500 mt-1">Current confirmed affiliate revenue</p>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Subscribers</p>
          <p className="text-2xl font-bold text-white mt-2">{adminData.subscribers.count}</p>
          <p className="text-xs text-slate-500 mt-1">Conversion rate {adminData.subscribers.conversion_rate}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <section className="xl:col-span-2 bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-2xl">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2"><ShieldAlert className="w-4 h-4 text-rose-400" /> Alert log</h2>
          <div className="space-y-3 mt-4">
            {adminData.alert_log.length === 0 ? (
              <div className="border border-dashed border-slate-700 rounded-xl p-6 text-sm text-slate-400">No runtime alerts captured yet.</div>
            ) : (
              adminData.alert_log.map((alert) => (
                <div key={alert.id} className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <Bell className="w-3.5 h-3.5" /> {alert.timestamp}
                  </div>
                  <p className="text-sm text-slate-200 mt-2 leading-relaxed">{alert.message}</p>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-2xl">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2"><LineChart className="w-4 h-4 text-cyan-400" /> Traffic baseline</h2>
          <div className="space-y-4 mt-4 text-sm text-slate-300">
            <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500">Daily visitors</p>
              <p className="text-xl font-semibold mt-2">{adminData.traffic.daily}</p>
            </div>
            <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500">Weekly visitors</p>
              <p className="text-xl font-semibold mt-2">{adminData.traffic.weekly}</p>
            </div>
            <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
              <p className="text-slate-500">Monthly visitors</p>
              <p className="text-xl font-semibold mt-2">{adminData.traffic.monthly}</p>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">Traffic cards intentionally stay at zero until a verified analytics integration exists.</p>
          </div>
        </section>
      </div>
    </div>
  );

  const renderTrendExplorer = () => (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2"><TrendingUp className="w-6 h-6 text-indigo-400" /> Trend explorer</h1>
          <p className="text-sm text-slate-400 mt-2">Public vs Premium visibility is enforced by the signed-in user tier. Only verified Reddit public JSON rows with provenance are shown as live.</p>
        </div>
        <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-300">
          <Search className="w-4 h-4 text-slate-500" /> {trends.length} verified Reddit trend records loaded
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => setTrendView('public')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold border ${trendView === 'public' ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-950 text-slate-300 border-slate-800'}`}
        >
          Public view
        </button>
        <button
          onClick={() => paidAccess && setTrendView('premium')}
          className={`px-4 py-2 rounded-xl text-sm font-semibold border flex items-center gap-2 ${trendView === 'premium' ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-950 text-slate-300 border-slate-800'} ${!paidAccess ? 'opacity-60 cursor-not-allowed' : ''}`}
        >
          <Lock className="w-4 h-4" /> Premium view
        </button>
        {!paidAccess && <span className="text-sm text-amber-300 self-center">Upgrade to Basic or Pro to open Premium results.</span>}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        <section className="xl:col-span-7 bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">{trendView === 'public' ? 'Public feed' : 'Premium feed'}</h2>
            {trendView === 'public' && hiddenPremiumCount > 0 && (
              <span className="text-xs text-slate-400">{hiddenPremiumCount} premium items hidden from free access</span>
            )}
          </div>

          <div className="divide-y divide-slate-900">
            {visibleTrends.length === 0 ? (
              <div className="p-8 text-sm text-slate-400 leading-relaxed">No verified Reddit public JSON trends available for this view yet. Seeded and simulated records remain withheld.</div>
            ) : (
              visibleTrends.map((trend) => (
                <button
                  key={trend.id}
                  onClick={() => setSelectedTrendId(trend.id)}
                  className={`w-full text-left p-4 transition ${trend.id === selectedTrendId ? 'bg-indigo-950/30' : 'hover:bg-slate-900/60'}`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className="w-11 h-11 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-300">
                        <Package className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold text-white">{trend.product.name}</h3>
                          <span className={`text-[10px] uppercase tracking-wider px-2 py-1 rounded-full border ${trend.access_level === 'premium' ? 'bg-amber-500/10 text-amber-300 border-amber-500/20' : 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20'}`}>
                            {trend.access_level}
                          </span>
                          {trend.locked && <span className="text-[10px] uppercase tracking-wider px-2 py-1 rounded-full border bg-rose-500/10 text-rose-300 border-rose-500/20">Locked</span>}
                        </div>
                        <p className="text-sm text-slate-400 mt-1">{trend.product.category} • Source: {trend.source_subreddit ? `r/${trend.source_subreddit}` : 'Reddit public JSON'}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm lg:text-right">
                      <div>
                        <p className="text-slate-500">Velocity</p>
                        <p className="font-semibold text-indigo-300">{trend.velocity_score.toFixed(1)}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">PIR</p>
                        <p className="font-semibold text-emerald-300">{(trend.purchase_intent_ratio * 100).toFixed(0)}%</p>
                      </div>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </section>

        <section className="xl:col-span-5 bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div>
              <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Selected trend</p>
              <h2 className="text-lg font-semibold text-white mt-1">{selectedTrend?.product.name ?? 'No trend selected'}</h2>
            </div>
            {selectedTrend && <span className={`text-xs px-2 py-1 rounded-full border ${selectedTrend.locked ? 'bg-rose-500/10 text-rose-300 border-rose-500/20' : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'}`}>{selectedTrend.locked ? 'Upgrade required' : 'Accessible'}</span>}
          </div>

          {selectedTrend && selectedDrafts ? (
            <div className="p-4 space-y-4">
              <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4">
                <p className="text-sm text-slate-300 leading-relaxed">{selectedTrend.product.description}</p>
              </div>

              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 text-sm">
                <p className="text-[10px] uppercase tracking-wider text-emerald-300 font-bold">Verified source provenance</p>
                <p className="text-emerald-50/90 mt-2">
                  Reddit public JSON • {selectedTrend.source_subreddit ? `r/${selectedTrend.source_subreddit}` : 'source subreddit recorded'} • {selectedTrend.source_ingest_method ?? 'reddit_public_json'}
                </p>
                {selectedTrend.source_url && (
                  <a href={selectedTrend.source_url} target="_blank" rel="noopener noreferrer" className="inline-block text-emerald-300 hover:text-emerald-200 mt-2">
                    Open Reddit source
                  </a>
                )}
              </div>

              {selectedTrend.locked ? (
                <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-5">
                  <div className="flex items-center gap-2 text-amber-300 font-semibold"><Lock className="w-4 h-4" /> Premium trend locked</div>
                  <p className="text-sm text-amber-100/80 mt-2 leading-relaxed">This trend belongs to the Premium feed. Upgrade the user record to Basic or Pro to unlock the analytics and copy workspace.</p>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-3 gap-2">
                    {(['blog', 'script', 'social'] as CopyType[]).map((type) => (
                      <button
                        key={type}
                        onClick={() => setCopyType(type)}
                        className={`py-2 rounded-xl text-xs font-semibold border ${copyType === type ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-900 text-slate-300 border-slate-800'}`}
                      >
                        {type === 'blog' ? 'Blog brief' : type === 'script' ? 'Video script' : 'Social copy'}
                      </button>
                    ))}
                  </div>

                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-2">Creator hooks</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedDrafts.keywords.map((keyword) => (
                        <span key={keyword} className="px-2 py-1 rounded-full bg-indigo-950/40 text-indigo-300 text-xs border border-indigo-500/20">#{keyword.replace(/\s+/g, '')}</span>
                      ))}
                    </div>
                  </div>

                  <ul className="space-y-2 text-sm text-slate-300 list-disc pl-5">
                    {selectedDrafts.features.map((feature) => (
                      <li key={feature}>{feature}</li>
                    ))}
                  </ul>

                  <textarea
                    readOnly
                    value={selectedDrafts[copyType]}
                    className="w-full h-64 bg-slate-900 border border-slate-800 rounded-xl p-4 text-sm text-slate-200 font-mono leading-relaxed resize-none"
                  />

                  <button
                    onClick={handleCopyDraft}
                    className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition flex items-center justify-center gap-2"
                  >
                    <Copy className="w-4 h-4" /> Copy selected draft
                  </button>
                </>
              )}
            </div>
          ) : (
            <div className="p-8 text-sm text-slate-400">Select a trend to inspect its details.</div>
          )}
        </section>
      </div>
    </div>
  );

  const renderSubscription = () => {
    const STRIPE_LINKS: Record<string, string> = {
      basic: 'https://buy.stripe.com/28EcN760Q44G22sffhbZe08',
      pro: 'https://buy.stripe.com/fZu6oJblaat422s1orbZe09'
    };

    return (
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <CreditCard className="w-6 h-6 text-indigo-400" /> Subscription
            </h1>
            <p className="text-sm text-slate-400 mt-2">Manage your subscription plan.</p>
          </div>
          <span className={`px-3 py-2 rounded-xl border text-sm font-semibold self-start ${tierBadgeColor(currentUser?.tier ?? 'free')}`}>
            Current tier: {(currentUser?.tier ?? 'free').toUpperCase()}
          </span>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 text-sm text-slate-300 leading-relaxed">
          {subscriptionData?.message ?? 'Upgrade to unlock premium trends.'}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {(subscriptionData?.plans ?? []).map((plan) => {
            const checkoutUrl = STRIPE_LINKS[plan.id];
            return (
              <section key={plan.id} className="bg-slate-950 border border-slate-800 rounded-2xl p-6 shadow-2xl flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">{plan.name}</p>
                      <h2 className="text-3xl font-bold text-white mt-2">${plan.price_monthly}<span className="text-base text-slate-400">/mo</span></h2>
                      <p className="text-sm text-slate-400 mt-2">{plan.description}</p>
                    </div>
                    {plan.id === 'pro' && <Crown className="w-8 h-8 text-amber-300 flex-shrink-0" />}
                  </div>
                  <ul className="space-y-2 mt-5 text-sm text-slate-300 list-disc pl-5">
                    {plan.features.map((feature) => <li key={feature}>{feature}</li>)}
                  </ul>
                </div>
                <div>
                  {currentUser?.tier === plan.id ? (
                    <button
                      disabled
                      className="mt-6 w-full bg-slate-900 border border-slate-800 text-slate-500 py-3 rounded-xl font-semibold cursor-default text-center"
                    >
                      Current plan
                    </button>
                  ) : checkoutUrl ? (
                    <a
                      href={checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-6 block w-full bg-indigo-600 hover:bg-indigo-500 text-white text-center font-semibold py-3 rounded-xl transition duration-200"
                    >
                      Upgrade to {plan.name} — ${plan.price_monthly}/mo
                    </a>
                  ) : null}
                </div>
              </section>
            );
          })}
        </div>

        <section className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-2xl">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <Zap className="w-4 h-4 text-cyan-400" /> Implementation notes
          </h2>
          <ul className="space-y-2 mt-4 text-sm text-slate-300 list-disc pl-5">
            {(subscriptionData?.notes ?? [
              'The app does not call Stripe directly.',
              'User access is gated by the database tier field.',
            ]).map((note) => <li key={note}>{note}</li>)}
          </ul>
        </section>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-slate-800 bg-slate-950/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-lg text-white">TrendCatcher</div>
              <div className="text-[11px] text-slate-500">Creator trend early-warning dashboard</div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className={`hidden sm:inline-flex px-3 py-1.5 rounded-full border text-xs font-semibold ${tierBadgeColor(currentUser?.tier ?? 'free')}`}>
              {(currentUser?.tier ?? 'free').toUpperCase()} tier
            </span>
            {currentUser ? (
              <>
                <div className="hidden md:block text-right">
                  <div className="text-sm font-semibold text-white">{currentUser.username}</div>
                  <div className="text-xs text-slate-500">{currentUser.email}</div>
                </div>
                <button onClick={handleLogout} className="bg-slate-900 hover:bg-slate-800 border border-slate-800 px-3 py-2 rounded-xl text-sm flex items-center gap-2">
                  <LogOut className="w-4 h-4" /> Sign out
                </button>
              </>
            ) : (
              <button onClick={() => setView('trends')} className="bg-slate-900 hover:bg-slate-800 border border-slate-800 px-3 py-2 rounded-xl text-sm">Public preview</button>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-6">
          <aside className="bg-slate-950 border border-slate-800 rounded-2xl p-4 h-fit shadow-2xl">
            <div className="space-y-2">
              <button onClick={() => setView('command')} className={`w-full px-4 py-3 rounded-xl text-sm font-semibold flex items-center gap-2 ${view === 'command' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-300 border border-slate-800'}`}>
                <LayoutDashboard className="w-4 h-4" /> Command dashboard
              </button>
              <button onClick={() => setView('trends')} className={`w-full px-4 py-3 rounded-xl text-sm font-semibold flex items-center gap-2 ${view === 'trends' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-300 border border-slate-800'}`}>
                <Sparkles className="w-4 h-4" /> Trend explorer
              </button>
              <button onClick={() => setView('subscription')} className={`w-full px-4 py-3 rounded-xl text-sm font-semibold flex items-center gap-2 ${view === 'subscription' ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-slate-300 border border-slate-800'}`}>
                <CreditCard className="w-4 h-4" /> Subscription
              </button>
            </div>

            <div className="mt-6 p-4 rounded-xl border border-slate-800 bg-slate-900/60">
              <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">Access policy</p>
              <p className="text-sm text-slate-300 mt-2 leading-relaxed">
                Free users can browse Public trends. Basic and Pro users unlock Premium trend results through the account tier stored in the database.
              </p>
            </div>
          </aside>

          <main>
            {!currentUser && view !== 'command' ? renderAuthShell() : view === 'command' ? renderCommandView() : view === 'trends' ? renderTrendExplorer() : renderSubscription()}
          </main>
        </div>
      </div>

      {toast.visible && (
        <div className="fixed bottom-6 right-6 bg-indigo-600 text-white px-4 py-3 rounded-xl shadow-2xl border border-indigo-400 text-sm font-semibold flex items-center gap-2 z-50">
          <CheckCircle2 className="w-4 h-4 text-emerald-300" />
          <span>{toast.message}</span>
        </div>
      )}
    </div>
  );
}
