import { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Search, 
  Bell, 
  Zap, 
  LayoutDashboard, 
  Compass, 
  Sparkles, 
  Globe, 
  ShieldAlert, 
  Smile, 
  Percent, 
  Package, 
  Video, 
  Image as ImageIcon, 
  MessageSquare, 
  CheckCircle2, 
  Link as LinkIcon, 
  UploadCloud, 
  Copy,
  LineChart
} from 'lucide-react';

// Define TS Types
interface Comment {
  user: string;
  text: string;
  platform: 'tiktok' | 'pinterest' | 'reddit';
}

interface CopyDraft {
  blog: string;
  script: string;
  social: string;
}

interface Product {
  id: string;
  name: string;
  category: string;
  price: string;
  velocity: number;
  pir: number;
  status: 'Emerging' | 'Viral' | 'Saturated';
  platforms: ('tiktok' | 'pinterest' | 'reddit')[];
  keywords: string[];
  features: string[];
  comments: Comment[];
  copy: CopyDraft;
}

// Local mock data as fallback to ensure the skeleton is robust & self-contained
const MOCK_PRODUCTS: Product[] = [
  {
    id: "prod-001",
    name: "Smart Galaxy Nebula Projector",
    category: "Smart Home / Lighting",
    price: "$49.99",
    velocity: 94,
    pir: 88,
    status: "Emerging",
    platforms: ["tiktok", "pinterest", "reddit"],
    keywords: ["galaxy nebula laser", "sky light app", "bedroom decor lighting", "christmas gift projector"],
    features: [
      "App-controlled custom celestial projections",
      "Voice integration with Alexa & Google Assistant",
      "Dynamic ambient mode reactive to ambient sound/music",
      "Ultra-silent motor design for restful sleep schedules"
    ],
    comments: [
      { user: "decor_lover_22", text: "Oh my god I need this for my bedroom immediately! Where is the link?", platform: "tiktok" },
      { user: "curious_george", text: "Ordered mine yesterday on Amazon. Stoked for it to arrive!", platform: "reddit" },
      { user: "pinterest_mom", text: "This is beautiful. Added to my aesthetic lighting inspo board.", platform: "pinterest" }
    ],
    copy: {
      blog: `## Honest Review: The Smart Galaxy Nebula Projector You Keep Seeing on Socials\n\nIf you have scrolled through TikTok or Pinterest recently, you have likely seen bedrooms transformed into breathtaking cosmic sanctuaries. The secret behind this gorgeous aesthetic is the **Smart Galaxy Nebula Projector**. Today we are breaking down why this smart decor is flying off virtual shelves.\n\n### Why It's Going Viral\nThe projector uses micro-laser technology to cast rich, high-definition nebula clouds and stars across your ceiling. Unlike older, clunky light models, this is app-controlled, meaning you can custom mix colors, dim brightness, and adjust rotation speed directly from your phone.\n\n### Key Features Evaluated\n- **Vast Customization:** Access over 16 million colors through the smart companion app.\n- **Sound Reactivity:** Ambient music integration syncs cloud pulses to the rhythm of your songs.\n- **Voice Control Compatible:** Connects effortlessly to Alexa and Google Home.\n\n### Conclusion & Affiliate Link\nThis viral product is a highly profitable niche to build affiliate campaigns on. Click below to secure the current discount:\n👉 [Get Yours From the Best Rated Vendor Here](https://amzn.to/3vE6mNP)`,
      script: `### TikTok/Reels Video Script - Galaxy Projector\n\n**[HOOK - 0:00 to 0:03]**\n*Visual:* Camera pans across a dark, completely boring bedroom. Suddenly, user clicks their fingers.\n*Audio / Voiceover:* "Stop scrolling unless you want to transform your room into a literal galaxy."\n\n**[BODY - 0:03 to 0:12]**\n*Visual:* Screen lights up with pulsing, gorgeous red and blue cosmic nebula waves on the ceiling. Show phone app changing color sliders.\n*Audio / Voiceover:* "This is the viral Galaxy Projector. It lets you customize 16 million colors from your phone, syncs to your music, and runs completely silent."\n\n**[CTA - 0:12 to 0:15]**\n*Visual:* Close-up of the tiny projector on a nightstand. Overlay text: "Link in bio for 40% off!"\n*Audio / Voiceover:* "Click the link in my bio to get yours before the sale ends today!"`,
      social: `📌 **Cosmic Bedroom Aesthetic Inspo**\n\nUnleash your inner stargazer with this smart app-controlled nebula projector. Perfect for movie nights, gamer rigs, or soothing sleep schedules. 🌌\n\n👉 Tap the pin to get yours for 40% off today! #bedroomgoals #roomaesthetic #amazonfinds #lightinginspo`
    }
  },
  {
    id: "prod-002",
    name: "Levitating Floating Bonsai Pot",
    category: "Home & Garden",
    price: "$74.50",
    velocity: 85,
    pir: 79,
    status: "Emerging",
    platforms: ["pinterest", "reddit"],
    keywords: ["levitating bonsai", "floating design pot", "futuristic home decor", "magnetic suspension plant"],
    features: [
      "Maglev magnetic levitation suspension technology",
      "360-degree rotation of standard houseplants",
      "Minimalist, clean Japanese zen-like aesthetic",
      "Integrated power adapter base for silent magnetic balance"
    ],
    comments: [
      { user: "garden_zen", text: "How does this magic work? Does it spin on its own? Sending this to my dad.", platform: "pinterest" },
      { user: "physics_nerd", text: "Incredibly cool application of magnetic induction levitation. Ordering.", platform: "reddit" }
    ],
    copy: {
      blog: `## Levitating Bonsai Tree Pot: Sci-Fi Tech Meets Zen Gardening\n\nThe **Levitating Floating Bonsai Pot** is a gorgeous statement piece that utilizes electromagnetic suspension to hover and spin a real plant in mid-air. It's the ultimate conversation-starter.\n\n### Features breakdown\n- **360 Rotation:** Steady magnetic fields rotate the plant, maximizing exposure to sunlight.\n- **Futuristic Zen:** Minimalist oak base fits into modern living rooms and executive desk setups.\n\n👉 [Buy the Levitating Floating Bonsai Pot on Amazon](https://amzn.to/3vLevPlant)`,
      script: `### TikTok/Reels Video Script - Levitating Bonsai\n\n**[HOOK - 0:00 to 0:03]**\n*Visual:* Hand gently spins a floating plant pot mid-air with no wires.\n*Audio:* "This floating plant is straight out of the year 3000!"\n\n**[BODY - 0:03 to 0:12]**\n*Audio:* "It uses actual magnets to hover and rotate your plants 360 degrees so they get even sunlight. Perfect for bonsai or small succulents."\n\n**[CTA - 0:12 to 0:15]**\n*Visual:* Text on screen: "Check out the link in my bio for a massive discount!"`,
      social: `📌 **Levitating Plant Pot - Magnetic Levitation Decor**\n\nBring your plants to life with this beautiful floating pot! 🌿 Hovering and spinning silently to add science-fiction elegance to any table.\n\n👉 Tap to shop directly from Amazon! #plantgoals #interiordesign #scienceart`
    }
  },
  {
    id: "prod-003",
    name: "Sunset Atmosphere Projection Lamp",
    category: "Aesthetic Room Decor",
    price: "$19.99",
    velocity: 72,
    pir: 68,
    status: "Viral",
    platforms: ["tiktok", "pinterest"],
    keywords: ["sunset projection lamp", "golden hour ring", "indie aesthetic room", "tiktok photo lighting"],
    features: [
      "Warm orange sunset projection halo with adjustable angle",
      "180-degree rotating iron bracket head",
      "Anti-glare optical crystal lens for photorealistic glows",
      "USB powered with stable base plate construction"
    ],
    comments: [
      { user: "indie_vibes", text: "The glow on my face is literally photorealistic. Unbelievable for golden hour pics.", platform: "tiktok" },
      { user: "decor_pin", text: "Perfect accessory for cozy reading corners.", platform: "pinterest" }
    ],
    copy: {
      blog: `## Review: Sunset Projection Lamp (Golden Hour Photo Secret)\n\nIf you have wondered how influencers get the perfect golden glow, the **Sunset Projection Lamp** is your answer. Casting a hyper-realistic warm sun ring, it turns blank white walls into artistic canvas.\n\n👉 [Claim Your Sunset Lamp Today](https://amzn.to/3vSunset)`,
      script: `### Video Script - Golden Hour Sunset Lamp\n\n**[HOOK]**\n"How to get the perfect sunset glow inside your room at any time of day."\n\n**[BODY]**\n"This small USB-powered lamp projects a flawless sunset circle. It rotates 180 degrees so you can angle it anywhere for portraits, backgrounds, or cozy reading."\n\n**[CTA]**\n"Get 50% off with the link in bio!"`,
      social: `📌 **Sunset projection lamp - Golden hour all day!**\n\nInstantly capture perfect aesthetic lighting in your bedroom or studio. ☀️\n\n👉 Tap link to shop on Amazon. #cozyvibes #aesthetic #sunsetlamp`
    }
  }
];

export default function App() {
  const [products, setProducts] = useState<Product[]>(MOCK_PRODUCTS);
  const [selectedId, setSelectedId] = useState<string>("prod-001");
  const [activeTab, setActiveTab] = useState<'signals' | 'copywriter'>('signals');
  const [copyType, setCopyType] = useState<'blog' | 'script' | 'social'>('blog');
  const [showNotifications, setShowNotifications] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [currentView, setCurrentView] = useState<'command' | 'overview'>('command');
  const [adminData, setAdminData] = useState<any>(null);

  useEffect(() => {
    const fetchAdminData = () => {
      fetch('/api/admin/dashboard')
        .then(res => res.json())
        .then(data => setAdminData(data))
        .catch(err => console.error("Error fetching admin dashboard data:", err));
    };
    fetchAdminData();
    const interval = setInterval(fetchAdminData, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  // Get unique list of categories dynamically from products
  const categories = ["All", ...Array.from(new Set(products.map(p => p.category)))];

  // Filtered products list based on selection
  const filteredProducts = selectedCategory === "All"
    ? products
    : products.filter(p => p.category === selectedCategory);
  
  // Toast Notification State
  const [toast, setToast] = useState<{ visible: boolean; message: string; icon: string }>({
    visible: false,
    message: '',
    icon: 'check-circle'
  });

  const selectedProduct = filteredProducts.find(p => p.id === selectedId) || filteredProducts[0] || products[0];

  // Fetch from FastAPI Backend on Mount (Progressive Enhancement)
  useEffect(() => {
    fetch('/api/products')
      .then(res => {
        if (res.ok) return res.json();
        throw new Error('Local fallback active');
      })
      .then(data => {
        // Hydrate mock schemas back to full Product structure
        const hydrated: Product[] = data.map((apiProd: any) => {
          const matchedMock = MOCK_PRODUCTS.find(p => p.name === apiProd.name) || MOCK_PRODUCTS[0];
          return {
            ...matchedMock,
            id: apiProd.id,
            name: apiProd.name,
            category: apiProd.category || matchedMock.category,
            price: apiProd.estimated_price ? `$${apiProd.estimated_price}` : matchedMock.price
          };
        });
        setProducts(hydrated);
      })
      .catch(() => {
        console.log("FastAPI backend skeleton offline. Using local high-fidelity mock data.");
      });
  }, []);

  const triggerToast = (message: string, icon: string = 'check-circle') => {
    setToast({ visible: true, message, icon });
    setTimeout(() => {
      setToast(prev => ({ ...prev, visible: false }));
    }, 3000);
  };

  const handleCopyText = () => {
    const textToCopy = selectedProduct.copy[copyType];
    navigator.clipboard.writeText(textToCopy);
    triggerToast("Draft copied to clipboard!", "copy");
  };

  return (
    <div className="bg-slate-900 text-slate-100 min-h-screen flex flex-col font-sans">
      
      {/* Top Navigation Global Header */}
      <header className="bg-slate-950 border-b border-slate-800 h-16 flex items-center justify-between px-6 z-10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg text-white">
            <TrendingUp className="w-6 h-6" />
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            TrendCatcher
          </span>
          <span className="bg-indigo-900/50 text-indigo-300 text-xs font-semibold px-2 py-0.5 rounded-full border border-indigo-800">
            PRO PLAN
          </span>
        </div>

        {/* Global Search Mockup */}
        <div className="hidden md:flex items-center bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 w-96">
          <Search className="w-4 h-4 text-slate-500 mr-2" />
          <input 
            type="text" 
            placeholder="Search products, hashtags, subreddits..." 
            className="bg-transparent text-sm text-slate-200 outline-none w-full placeholder-slate-600"
          />
        </div>

        {/* Notifications & Quick Scan */}
        <div className="flex items-center gap-4">
          <button 
            onClick={() => triggerToast("Crawlers triggered! Querying social metrics...", "zap")}
            className="bg-slate-900 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-950 text-xs font-semibold px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition"
          >
            <Zap className="w-3.5 h-3.5" /> Quick Scan
          </button>

          {/* Alert Bell */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="hover:bg-slate-800 p-2 rounded-full transition text-slate-300 relative"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 bg-rose-500 w-2 h-2 rounded-full"></span>
            </button>
            
            {showNotifications && (
              <div className="absolute right-0 mt-3 w-80 bg-slate-950 border border-slate-800 rounded-xl shadow-2xl p-4 text-xs z-50">
                <h4 className="font-bold text-slate-200 mb-2 pb-2 border-b border-slate-800 flex justify-between items-center">
                  Recent Signals <span className="text-[10px] bg-rose-500/20 text-rose-400 px-1.5 py-0.5 rounded-full">3 Alerts</span>
                </h4>
                <div className="space-y-3">
                  <div className="p-2 bg-slate-900 rounded-lg border-l-2 border-green-500">
                    <span className="font-semibold text-slate-300">TikTok Trend Alert:</span>
                    <p className="text-slate-400 mt-0.5">#SunsetLamp views spiked +210% in last 12 hours.</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 border-l border-slate-800 pl-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 flex items-center justify-center text-xs font-bold text-white shadow">
              ME
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-xs font-semibold text-slate-200">Marketing Team</div>
              <div className="text-[10px] text-slate-500">admin@trendcatcher.io</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Workspace Layout */}
      <div className="flex flex-1 overflow-hidden">
        
        {/* Sidebar Navigation */}
        <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col justify-between p-4 shrink-0 hidden md:flex">
          <div className="space-y-6">
            <nav className="space-y-1">
              <button 
                onClick={() => setCurrentView('command')} 
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg font-medium text-sm transition ${currentView === 'command' ? 'bg-indigo-600/10 text-indigo-400 border-l-2 border-indigo-500' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'}`}
              >
                <LayoutDashboard className="w-4 h-4" /> Command Dashboard
              </button>
              <button 
                onClick={() => setCurrentView('overview')} 
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg font-medium text-sm transition ${currentView === 'overview' ? 'bg-indigo-600/10 text-indigo-400 border-l-2 border-indigo-500' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'}`}
              >
                <Compass className="w-4 h-4" /> Trend Explorer
              </button>
            </nav>

            <div>
              <h5 className="text-[10px] font-bold text-slate-500 tracking-wider uppercase px-3 mb-2">Monitor Channels</h5>
              <div className="space-y-1.5 px-3">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5"><Video className="w-3.5 h-3.5 text-rose-400" /> TikTok Scraper</span>
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5"><ImageIcon className="w-3.5 h-3.5 text-red-500" /> Pinterest Scraper</span>
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5"><MessageSquare className="w-3.5 h-3.5 text-orange-400" /> Reddit Parser</span>
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-3 bg-slate-900/50 rounded-xl border border-slate-800">
            <div className="flex justify-between items-center text-xs mb-1.5">
              <span className="text-slate-400">Scrape API Usage</span>
              <span className="font-semibold">3.2k / 10k</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5">
              <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: '32%' }}></div>
            </div>
            <span className="text-[9px] text-slate-500 mt-2 block">Resets in 11 days</span>
          </div>
        </aside>

        {/* Main Panel Canvas */}
        <main className="flex-1 flex flex-col overflow-y-auto bg-slate-900">
          <div className="p-6 space-y-6 flex-1 flex flex-col justify-between">
            {currentView === 'command' ? (
              <div className="space-y-6 flex-1 flex flex-col justify-between">
                {/* Command Dashboard Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                      <LayoutDashboard className="w-6 h-6 text-indigo-400" /> Command Dashboard
                    </h1>
                    <p className="text-xs text-slate-400">TrendCatcher Unified Administrative Control Panel & Live Infrastructure Monitor.</p>
                  </div>
                  <div className="text-xs text-slate-400 flex items-center gap-3 bg-slate-950 border border-slate-800 px-4 py-2 rounded-xl shadow-lg">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Control Center Online
                    </span>
                    <span className="text-slate-700">|</span>
                    <span>Refreshed: <strong>Just Now</strong></span>
                  </div>
                </div>

                {/* Live Process Health Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl flex items-center justify-between shadow-lg relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Port 3000 SaaS Server</span>
                      <span className="text-sm font-semibold text-white mt-1 block">FastAPI Web Application</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`w-3 h-3 rounded-full ${adminData?.process_health?.saas_server === 'green' ? 'bg-emerald-500' : 'bg-red-500'} shadow-lg shadow-emerald-500/30`}></span>
                      <span className="text-xs font-bold text-slate-300 uppercase">{adminData?.process_health?.saas_server === 'green' ? 'Active' : 'Offline'}</span>
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl flex items-center justify-between shadow-lg relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-cyan-500"></div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Port 5000 Blog Server</span>
                      <span className="text-sm font-semibold text-white mt-1 block">Express Node.js Platform</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`w-3 h-3 rounded-full ${adminData?.process_health?.blog_server === 'green' ? 'bg-emerald-500' : 'bg-red-500'} shadow-lg shadow-emerald-500/30`}></span>
                      <span className="text-xs font-bold text-slate-300 uppercase">{adminData?.process_health?.blog_server === 'green' ? 'Active' : 'Offline'}</span>
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl flex items-center justify-between shadow-lg relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Scheduler Daemon</span>
                      <span className="text-sm font-semibold text-white mt-1 block">Autonomous Python Scraper</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`w-3 h-3 rounded-full ${adminData?.process_health?.scheduler_daemon === 'green' ? 'bg-emerald-500' : 'bg-red-500'} shadow-lg shadow-emerald-500/30`}></span>
                      <span className="text-xs font-bold text-slate-300 uppercase">{adminData?.process_health?.scheduler_daemon === 'green' ? 'Active' : 'Offline'}</span>
                    </div>
                  </div>
                </div>

                {/* Financial & Content Cards */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Total Revenue</span>
                      <span className="text-2xl font-extrabold text-white">${adminData?.revenue?.total ? adminData.revenue.total.toLocaleString() : '9,090.50'}</span>
                      <span className="text-[10px] text-emerald-400 flex items-center mt-0.5 gap-0.5"><TrendingUp className="w-3 h-3" /> Stripe Live Synced</span>
                    </div>
                    <div className="bg-indigo-600/10 p-2.5 rounded-lg text-indigo-400">
                      <LayoutDashboard className="w-6 h-6" />
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">SaaS MRR Tiers</span>
                      <span className="text-2xl font-extrabold text-white">${adminData?.revenue?.saas_mrr ? adminData.revenue.saas_mrr.toLocaleString() : '5,240.00'}</span>
                      <span className="text-[10px] text-slate-500 block mt-0.5">Basic + Pro subscriptions</span>
                    </div>
                    <div className="bg-cyan-600/10 p-2.5 rounded-lg text-cyan-400">
                      <Zap className="w-6 h-6" />
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Affiliate Income</span>
                      <span className="text-2xl font-extrabold text-white">${adminData?.revenue?.affiliate ? adminData.revenue.affiliate.toLocaleString() : '3,850.50'}</span>
                      <span className="text-[10px] text-emerald-400 flex items-center mt-0.5 gap-0.5"><TrendingUp className="w-3 h-3" /> Amazon / ShareASale</span>
                    </div>
                    <div className="bg-emerald-600/10 p-2.5 rounded-lg text-emerald-400">
                      <Smile className="w-6 h-6" />
                    </div>
                  </div>

                  <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                    <div>
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Email Subscribers</span>
                      <span className="text-2xl font-extrabold text-white">{adminData?.subscribers?.count || 0} Users</span>
                      <span className="text-[10px] text-indigo-400 block mt-0.5">{adminData?.subscribers?.conversion_rate || '3.5%'} conversion rate</span>
                    </div>
                    <div className="bg-amber-600/10 p-2.5 rounded-lg text-amber-400">
                      <Percent className="w-6 h-6" />
                    </div>
                  </div>
                </div>

                {/* Split Grid for Logs and Top Content */}
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 flex-1">
                  {/* Left Area: Traffic & Alerts */}
                  <div className="xl:col-span-7 flex flex-col gap-6">
                    
                    {/* Traffic Logs Card */}
                    <section className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-col shadow-2xl">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
                          <LineChart className="w-4 h-4 text-cyan-400" /> Web Traffic Logs
                        </h3>
                        <div className="flex gap-4 text-[10px] text-slate-400 font-semibold bg-slate-900 px-3 py-1 rounded-lg">
                          <span>Daily: <strong className="text-white">{adminData?.traffic?.daily || 1420}</strong></span>
                          <span>Weekly: <strong className="text-white">{adminData?.traffic?.weekly || 9850}</strong></span>
                          <span>Monthly: <strong className="text-white">{adminData?.traffic?.monthly || 41200}</strong></span>
                        </div>
                      </div>
                      
                      {/* Traffic history bar representation */}
                      <div className="h-44 w-full flex items-end justify-between bg-slate-950/40 rounded-xl p-4 border border-slate-900/60 relative">
                        <div className="absolute inset-0 flex flex-col justify-between p-4 pointer-events-none text-[9px] text-slate-600">
                          <div className="border-b border-slate-900 w-full pb-0.5">5,000 max</div>
                          <div className="border-b border-slate-900 w-full pb-0.5">2,500 mid</div>
                          <div className="w-full">0 min</div>
                        </div>
                        
                        {adminData?.traffic?.history?.map((hist: any, index: number) => {
                          const hPercent = (hist.visitors / 2500) * 100;
                          return (
                            <div key={index} className="flex flex-col items-center gap-1.5 z-10 w-full">
                              <div className="text-[9px] font-mono text-cyan-400 font-bold opacity-0 hover:opacity-100 transition duration-150 absolute -translate-y-8 bg-slate-900 border border-slate-800 px-1.5 py-0.5 rounded shadow">
                                {hist.visitors}
                              </div>
                              <div className="w-8 bg-gradient-to-t from-indigo-600 to-cyan-500 rounded-md hover:from-indigo-500 hover:to-cyan-400 transition" style={{ height: `${Math.min(100, hPercent)}px` }}></div>
                              <span className="text-[10px] text-slate-500 font-semibold font-mono">{hist.date}</span>
                            </div>
                          );
                        })}
                      </div>
                    </section>

                    {/* Live Active Alert Log */}
                    <section className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-col shadow-2xl flex-1 max-h-[300px] overflow-hidden">
                      <h3 className="font-bold text-sm text-slate-200 mb-3 flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 text-rose-500" /> Active System Alert Log (Live Log Parser)
                      </h3>
                      <div className="space-y-2 overflow-y-auto flex-1 pr-1" style={{ maxHeight: '200px' }}>
                        {adminData?.alert_log?.map((alert: any, index: number) => (
                          <div key={index} className="p-2.5 bg-slate-900/50 rounded-xl border border-slate-900 flex items-start gap-2.5 text-[11px] leading-relaxed">
                            <span className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${alert.type === 'error' ? 'bg-red-500' : alert.type === 'warning' ? 'bg-yellow-500' : alert.type === 'success' ? 'bg-emerald-500' : 'bg-blue-400'}`}></span>
                            <span className="font-mono text-slate-500 shrink-0 font-bold">{alert.timestamp}</span>
                            <p className="text-slate-300 font-medium break-all">{alert.message}</p>
                          </div>
                        ))}
                      </div>
                    </section>

                  </div>

                  {/* Right Area: Performance Cards */}
                  <div className="xl:col-span-5 flex flex-col gap-6">
                    
                    {/* Top Performing Posts */}
                    <section className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-col shadow-2xl">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
                          <Package className="w-4 h-4 text-emerald-400" /> Top Performing Posts by Revenue
                        </h3>
                        <span className="text-[9px] bg-emerald-500/10 text-emerald-400 font-bold px-2 py-0.5 rounded border border-emerald-500/20">LIVE METRICS</span>
                      </div>

                      <div className="divide-y divide-slate-900 overflow-y-auto max-h-[320px] pr-1">
                        {adminData?.top_performing_posts?.map((post: any, index: number) => (
                          <div key={index} className="py-2.5 flex justify-between items-center gap-3">
                            <div className="flex items-center gap-2.5 min-w-0">
                              <div className="w-6 h-6 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-[10px] text-slate-400 font-bold shrink-0">
                                #{index + 1}
                              </div>
                              <div className="min-w-0">
                                <span className="font-bold text-slate-300 text-xs truncate block">{post.title}</span>
                                <span className="text-[10px] text-slate-500 uppercase font-mono font-bold tracking-wider">{post.category} &bull; {post.views.toLocaleString()} views</span>
                              </div>
                            </div>
                            <div className="text-right shrink-0">
                              <span className="font-extrabold text-emerald-400 text-xs block">${post.revenue.toLocaleString()}</span>
                              <span className="text-[9px] text-slate-500 block font-semibold">{post.conversions} conversions</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>

                    {/* Content Status published vs scheduled */}
                    <section className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-col shadow-2xl">
                      <h3 className="font-bold text-sm text-slate-200 mb-3 flex items-center gap-2">
                        <Globe className="w-4 h-4 text-indigo-400" /> Content Publication Status
                      </h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-900 text-center">
                          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Published Posts</span>
                          <span className="text-2xl font-extrabold text-white mt-1 block">{adminData?.content_status?.published || 12}</span>
                          <span className="text-[10px] text-emerald-400 block mt-0.5">Live on Niche Site</span>
                        </div>
                        <div className="p-3 bg-slate-900/40 rounded-xl border border-slate-900 text-center">
                          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Scheduled Posts</span>
                          <span className="text-2xl font-extrabold text-white mt-1 block">{adminData?.content_status?.scheduled || 8}</span>
                          <span className="text-[10px] text-cyan-400 block mt-0.5">Queued in Buffer</span>
                        </div>
                      </div>
                    </section>

                  </div>
                </div>

                {/* Command Footer */}
                <footer className="text-center text-[10px] text-slate-500 pt-6 border-t border-slate-800">
                  TrendCatcher Automated Intelligence Engine &copy; 2026. Configured on Port 3000 bound live.
                </footer>
              </div>
            ) : (
              <div className="space-y-6 flex-1 flex flex-col justify-between">
                {/* Page Header Area */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">Overview Dashboard</h1>
                <p className="text-xs text-slate-400">Live viral tracking indicators & AI affiliate generation workspace.</p>
              </div>
              <div className="text-xs text-slate-400 flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg shadow-sm">
                <span className="w-2 h-2 rounded-full bg-green-500"></span> Engine Active
                <span className="text-slate-600">|</span>
                <span>Latest Scan: <strong>Just Now</strong></span>
              </div>
            </div>

            {/* KPI Cards row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Active Warnings</span>
                  <span className="text-2xl font-extrabold text-white">14</span>
                  <span className="text-[10px] text-emerald-400 flex items-center mt-0.5 gap-0.5"><TrendingUp className="w-3 h-3" /> +3 this week</span>
                </div>
                <div className="bg-indigo-600/10 p-2.5 rounded-lg text-indigo-400">
                  <ShieldAlert className="w-6 h-6" />
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Avg Velocity</span>
                  <span className="text-2xl font-extrabold text-white">87.2%</span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">Across top trends</span>
                </div>
                <div className="bg-cyan-600/10 p-2.5 rounded-lg text-cyan-400">
                  <Zap className="w-6 h-6" />
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Avg PIR Sentiment</span>
                  <span className="text-2xl font-extrabold text-white">84.1%</span>
                  <span className="text-[10px] text-emerald-400 flex items-center mt-0.5 gap-0.5"><TrendingUp className="w-3 h-3" /> Highly favorable</span>
                </div>
                <div className="bg-emerald-600/10 p-2.5 rounded-lg text-emerald-400">
                  <Smile className="w-6 h-6" />
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl flex items-center justify-between shadow-lg">
                <div>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">Campaign CTR</span>
                  <span className="text-2xl font-extrabold text-white">4.8%</span>
                  <span className="text-[10px] text-emerald-400 flex items-center mt-0.5 gap-0.5"><TrendingUp className="w-3 h-3" /> +1.2% above avg</span>
                </div>
                <div className="bg-amber-600/10 p-2.5 rounded-lg text-amber-400">
                  <Percent className="w-6 h-6" />
                </div>
              </div>
            </div>

            {/* Split Board Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 flex-1">
              
              {/* Left Column - Live Board */}
              <section className="xl:col-span-7 bg-slate-950 border border-slate-800 rounded-2xl flex flex-col shadow-2xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 flex justify-between items-center">
                  <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
                    <Package className="w-4 h-4 text-indigo-400" /> Emerging Viral Products (Live Board)
                  </h3>
                  <span className="text-[10px] bg-indigo-500/10 text-indigo-400 font-semibold px-2 py-0.5 rounded border border-indigo-500/20">AUTO-UPDATES ON</span>
                </div>

                {/* Categories Tab Navigation */}
                <div className="flex gap-1.5 p-3 px-4 border-b border-slate-900 overflow-x-auto bg-slate-950/40 select-none">
                  {categories.map(cat => (
                    <button
                      key={cat}
                      onClick={() => {
                        setSelectedCategory(cat);
                        // Auto-select first product in this category
                        const firstInCat = cat === "All" ? products[0] : products.find(p => p.category === cat);
                        if (firstInCat) setSelectedId(firstInCat.id);
                      }}
                      className={`text-[10px] font-semibold px-3 py-1.5 rounded-full border transition whitespace-nowrap ${
                        selectedCategory === cat
                          ? 'bg-indigo-600/20 text-indigo-400 border-indigo-500/40'
                          : 'bg-slate-900/50 text-slate-400 border-slate-800 hover:text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>

                <div className="overflow-x-auto flex-1">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-800 bg-slate-900/30">
                        <th className="p-4">Product Details</th>
                        <th className="p-4">Signals</th>
                        <th className="p-4">Velocity</th>
                        <th className="p-4">PIR</th>
                        <th className="p-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-900 text-xs">
                      {filteredProducts.map(prod => {
                        const isSelected = prod.id === selectedId;
                        return (
                          <tr 
                            key={prod.id} 
                            onClick={() => setSelectedId(prod.id)}
                            className={`cursor-pointer hover:bg-slate-900/50 transition border-b border-slate-900 ${isSelected ? 'bg-indigo-950/20' : ''}`}
                          >
                            <td className="p-4 flex items-center gap-3">
                              <div className="w-10 h-10 bg-slate-850 rounded-lg flex items-center justify-center text-slate-500 border border-slate-800">
                                <Package className="w-5 h-5" />
                              </div>
                              <div>
                                <div className="font-bold text-slate-200 hover:text-indigo-400 transition">{prod.name}</div>
                                <div className="text-[10px] text-slate-500">{prod.category} &bull; {prod.price}</div>
                              </div>
                            </td>
                            <td className="p-4">
                              <div className="flex gap-1">
                                {prod.platforms.includes('tiktok') && <span className="bg-rose-500/10 text-rose-400 p-1 rounded"><Video className="w-3.5 h-3.5" /></span>}
                                {prod.platforms.includes('pinterest') && <span className="bg-red-500/10 text-red-400 p-1 rounded"><ImageIcon className="w-3.5 h-3.5" /></span>}
                                {prod.platforms.includes('reddit') && <span className="bg-orange-500/10 text-orange-400 p-1 rounded"><MessageSquare className="w-3.5 h-3.5" /></span>}
                              </div>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                  <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${prod.velocity}%` }}></div>
                                </div>
                                <span className="font-bold text-slate-300">{prod.velocity}%</span>
                              </div>
                            </td>
                            <td className="p-4">
                              <span className="font-semibold text-emerald-400">{prod.pir}%</span>
                            </td>
                            <td className="p-4 text-right">
                              <button 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedId(prod.id);
                                  setActiveTab('copywriter');
                                }}
                                className="bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/50 text-slate-300 hover:text-indigo-400 text-[10px] font-bold px-2.5 py-1 rounded transition"
                              >
                                Draft Content
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </section>

              {/* Right Column - Workspace */}
              <section className="xl:col-span-5 bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
                <div className="p-4 bg-slate-900/40 border-b border-slate-800 flex justify-between items-center">
                  <div>
                    <span className="text-[10px] text-indigo-400 font-bold tracking-wider uppercase block">Active Workspace</span>
                    <h3 className="font-bold text-sm text-white">{selectedProduct.name}</h3>
                  </div>
                  <span className="bg-indigo-500/20 text-indigo-300 text-[10px] px-2 py-0.5 rounded font-semibold">
                    {selectedProduct.category}
                  </span>
                </div>

                {/* Workspace Tab Header */}
                <div className="bg-slate-900/10 border-b border-slate-800 flex text-xs font-semibold">
                  <button 
                    onClick={() => setActiveTab('signals')}
                    className={`flex-1 py-3 text-center border-b-2 flex items-center justify-center gap-1.5 transition ${activeTab === 'signals' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
                  >
                    <LineChart className="w-3.5 h-3.5" /> Signals Analytics
                  </button>
                  <button 
                    onClick={() => setActiveTab('copywriter')}
                    className={`flex-1 py-3 text-center border-b-2 flex items-center justify-center gap-1.5 transition ${activeTab === 'copywriter' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
                  >
                    <Sparkles className="w-3.5 h-3.5" /> AI Copywriter
                  </button>
                </div>

                {/* Tab Display container */}
                <div className="p-4 flex-1 overflow-y-auto space-y-4" style={{ maxHeight: '520px' }}>
                  
                  {activeTab === 'signals' ? (
                    <div className="space-y-4">
                      <div className="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
                        <div className="flex justify-between items-center mb-1.5">
                          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wide">Rolling 7-Day Velocity</span>
                          <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                            <TrendingUp className="w-3 h-3" /> Skyrocketing (Day 7: {selectedProduct.velocity}%)
                          </span>
                        </div>
                        
                        {/* Custom CSS Styled Mini Chart SVG representation */}
                        <div className="h-32 w-full flex items-end relative overflow-hidden bg-slate-950/20 rounded-lg p-2">
                          <svg viewBox="0 0 400 120" className="w-full h-full overflow-visible">
                            <defs>
                              <linearGradient id="reactGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.3"/>
                                <stop offset="100%" stopColor="#4f46e5" stopOpacity="0"/>
                              </linearGradient>
                            </defs>
                            <polyline 
                              points={`0,${120 - ((selectedProduct.velocity-20)/100*100)} 100,${120 - ((selectedProduct.velocity-15)/100*100)} 200,${120 - ((selectedProduct.velocity-8)/100*100)} 300,${120 - ((selectedProduct.velocity-5)/100*100)} 400,${120 - (selectedProduct.velocity/100*100)}`} 
                              fill="none" 
                              stroke="#6366f1" 
                              strokeWidth="2.5" 
                            />
                            <polygon 
                              points={`0,120 0,${120 - ((selectedProduct.velocity-20)/100*100)} 100,${120 - ((selectedProduct.velocity-15)/100*100)} 200,${120 - ((selectedProduct.velocity-8)/100*100)} 300,${120 - ((selectedProduct.velocity-5)/100*100)} 400,${120 - (selectedProduct.velocity/100*100)} 400,120`} 
                              fill="url(#reactGradient)" 
                            />
                            <circle cx="400" cy={120 - (selectedProduct.velocity/100*100)} r="4" fill="#6366f1" />
                          </svg>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">High-Intent Comments Extracted</h4>
                        <div className="space-y-2">
                          {selectedProduct.comments.map((com, idx) => (
                            <div key={idx} className="p-2 bg-slate-900 rounded-xl border border-slate-800 text-[11px] leading-relaxed relative">
                              <div className="flex items-center gap-1.5 mb-1">
                                <span className={`p-0.5 rounded text-xs ${com.platform === 'tiktok' ? 'bg-rose-500/10 text-rose-400' : com.platform === 'pinterest' ? 'bg-red-500/10 text-red-400' : 'bg-orange-500/10 text-orange-400'}`}>
                                  {com.platform === 'tiktok' ? <Video className="w-3 h-3" /> : com.platform === 'pinterest' ? <ImageIcon className="w-3 h-3" /> : <MessageSquare className="w-3 h-3" />}
                                </span>
                                <span className="font-bold text-slate-400">@{com.user}</span>
                                <span className="text-[9px] text-slate-500">Intent Detected</span>
                              </div>
                              <p className="text-slate-300 font-medium">"{com.text}"</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Extracted Key Features</h4>
                        <ul className="space-y-1.5 list-disc pl-4 text-xs text-slate-300">
                          {selectedProduct.features.map((feat, idx) => (
                            <li key={idx}>{feat}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Copy Draft Toggle Type */}
                      <div className="grid grid-cols-3 gap-2">
                        <button 
                          onClick={() => setCopyType('blog')}
                          className={`py-2 rounded-lg font-bold text-[10px] border transition ${copyType === 'blog' ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'}`}
                        >
                          Blog Review
                        </button>
                        <button 
                          onClick={() => setCopyType('script')}
                          className={`py-2 rounded-lg font-bold text-[10px] border transition ${copyType === 'script' ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'}`}
                        >
                          Video Script
                        </button>
                        <button 
                          onClick={() => setCopyType('social')}
                          className={`py-2 rounded-lg font-bold text-[10px] border transition ${copyType === 'social' ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'}`}
                        >
                          Social Pin
                        </button>
                      </div>

                      <div className="p-2.5 bg-slate-900/50 rounded-xl border border-slate-800 space-y-1">
                        <span className="text-[9px] text-slate-500 font-bold uppercase block">Target SEO Keywords Extracted</span>
                        <div className="flex flex-wrap gap-1">
                          {selectedProduct.keywords.map((kw, idx) => (
                            <span key={idx} className="text-[9px] bg-indigo-950/30 text-indigo-400 border border-indigo-500/20 font-mono px-2 py-0.5 rounded-full">
                              #{kw.replace(/\s+/g, '')}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="relative">
                        <span className="absolute top-2 right-2 text-[9px] bg-indigo-900/40 text-indigo-300 px-1.5 py-0.5 rounded font-mono font-bold">DRAFT READY</span>
                        <textarea 
                          readOnly
                          value={selectedProduct.copy[copyType]}
                          className="w-full h-72 bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 font-mono outline-none focus:border-indigo-500 resize-none overflow-y-auto leading-relaxed"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-2">
                        <button 
                          onClick={() => triggerToast("Amazon Associate tag tag='trendcatcher-20' injected!", "link")}
                          className="bg-slate-900 border border-slate-800 text-slate-200 hover:bg-slate-850 hover:text-white font-bold text-xs py-2 px-3 rounded-lg flex items-center justify-center gap-1.5 transition"
                        >
                          <LinkIcon className="w-3.5 h-3.5 text-indigo-400" /> Insert Affiliate Links
                        </button>
                        <button 
                          onClick={() => triggerToast("Post synced & published successfully to connected WordPress!", "upload-cloud")}
                          className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2 px-3 rounded-lg flex items-center justify-center gap-1.5 shadow transition"
                        >
                          <UploadCloud className="w-3.5 h-3.5" /> Publish to Site
                        </button>
                      </div>
                      
                      <button 
                        onClick={handleCopyText}
                        className="w-full bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-850 text-[10px] font-semibold py-1.5 px-3 rounded-lg flex items-center justify-center gap-1 transition"
                      >
                        <Copy className="w-3 h-3" /> Copy raw markdown content to clipboard
                      </button>
                    </div>
                  )}

                </div>
              </section>

            </div>

            <footer className="text-center text-[10px] text-slate-500 pt-6 border-t border-slate-800">
              TrendCatcher Automated Intelligence Engine &copy; 2026. Configured on Port 3000 bound live.
            </footer>
              </div>
            )}
          </div>
        </main>

      </div>

      {/* Toast banner */}
      {toast.visible && (
        <div className="fixed bottom-6 right-6 bg-indigo-600 text-slate-100 px-4 py-3 rounded-xl shadow-2xl border border-indigo-400 text-xs font-semibold flex items-center gap-2 z-50">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>{toast.message}</span>
        </div>
      )}

    </div>
  );
}
