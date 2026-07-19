import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, BookOpen, Code, Video, Database, Terminal, ArrowRight } from 'lucide-react';

export default function LandingPage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleTopicClick = (topic: string) => {
    navigate(`/search?q=${encodeURIComponent(topic)}`);
  };

  const popularTopics = [
    { name: 'Python', icon: <Terminal className="w-4 h-4" /> },
    { name: 'React', icon: <Code className="w-4 h-4" /> },
    { name: 'FastAPI', icon: <BookOpen className="w-4 h-4" /> },
    { name: 'Machine Learning', icon: <Database className="w-4 h-4" /> },
    { name: 'TypeScript', icon: <Code className="w-4 h-4" /> }
  ];

  const features = [
    {
      title: "GitHub Repositories",
      desc: "Discover repositories, awesome lists, and open source projects instantly.",
      icon: <Code className="w-6 h-6 text-indigo-400" />
    },
    {
      title: "YouTube Tutorials",
      desc: "Access structured playlists and learning videos normalized in one place.",
      icon: <Video className="w-6 h-6 text-purple-400" />
    },
    {
      title: "Google Books",
      desc: "Find references, programming textbooks, and learning guides.",
      icon: <BookOpen className="w-6 h-6 text-cyan-400" />
    },
    {
      title: "Hugging Face Datasets",
      desc: "Incorporate actual data sources and machine learning datasets.",
      icon: <Database className="w-6 h-6 text-emerald-400" />
    }
  ];

  return (
    <div className="relative min-h-screen flex flex-col justify-between overflow-hidden">
      
      {/* Background Animated Gradient Blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px] animate-pulse pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px] animate-pulse pointer-events-none" style={{ animationDelay: '2s' }} />

      {/* Header / Navbar */}
      <header className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-cyan-500 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
            LH
          </div>
          <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            LearnHub
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/login')}
            className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
          >
            Sign In
          </button>
          <button 
            onClick={() => navigate('/register')}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-lg shadow-indigo-600/20 hover:shadow-indigo-600/35 hover:-translate-y-0.5 active:translate-y-0"
          >
            Get Started
          </button>
        </div>
      </header>

      {/* Main Hero Container */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 py-12 max-w-5xl mx-auto text-center w-full">
        
        {/* Animated Feature Tag */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 backdrop-blur-md text-xs font-semibold text-indigo-400 mb-8"
        >
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
          </span>
          Next-gen Learning Aggregator Platform
        </motion.div>

        {/* Hero Title */}
        <motion.h1 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-b from-white via-slate-100 to-slate-400 bg-clip-text text-transparent leading-none"
        >
          Aggregate Your Learning<br/>
          <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
            One Single Search
          </span>
        </motion.h1>

        {/* Hero Subtitle */}
        <motion.p 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 font-normal leading-relaxed"
        >
          Stop browsing a dozen platforms. We query GitHub Awesome Lists, StackOverflow questions, Google Books, Hugging Face datasets, and YouTube playlists instantly.
        </motion.p>

        {/* Dynamic Search Bar */}
        <motion.form 
          onSubmit={handleSearch}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="w-full max-w-2xl relative mb-6"
        >
          <div className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 rounded-2xl blur opacity-30 group-hover:opacity-40 transition duration-1000 group-focus-within:opacity-50" />
            <div className="relative flex items-center bg-slate-900/90 border border-slate-700/80 rounded-2xl overflow-hidden backdrop-blur-xl">
              <Search className="w-6 h-6 text-slate-400 ml-4 pointer-events-none" />
              <input
                type="text"
                placeholder="What do you want to learn today? (e.g. FastAPI, Machine Learning)"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full bg-transparent px-4 py-4 md:py-5 text-slate-100 placeholder-slate-500 focus:outline-none text-base"
              />
              <button
                type="submit"
                className="mr-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium px-5 py-2.5 rounded-xl transition-all shadow-md flex items-center gap-2 group/btn"
              >
                Search <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
              </button>
            </div>
          </div>
        </motion.form>

        {/* Popular Topics */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="flex flex-wrap justify-center items-center gap-3 mb-16 text-sm text-slate-500"
        >
          <span>Popular:</span>
          {popularTopics.map((topic) => (
            <button
              key={topic.name}
              onClick={() => handleTopicClick(topic.name)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/40 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-all"
            >
              {topic.icon}
              {topic.name}
            </button>
          ))}
        </motion.div>

        {/* Statistics Grid */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 w-full mb-20 border-t border-b border-slate-800/80 py-8"
        >
          <div>
            <div className="text-3xl font-extrabold text-white">5+</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">Aggregated APIs</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-white">100%</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">No-Ads / Free</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-white">Instant</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">Unified Search</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-white">Cached</div>
            <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">Postgres Layer</div>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full text-left">
          {features.map((feat, idx) => (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * idx }}
              whileHover={{ y: -5 }}
              className="glass-card p-6 flex gap-4 hover:border-indigo-500/30 group"
            >
              <div className="w-12 h-12 rounded-xl bg-slate-800/85 border border-slate-700/50 flex items-center justify-center shrink-0 shadow-inner group-hover:scale-110 transition-transform">
                {feat.icon}
              </div>
              <div>
                <h3 className="text-lg font-bold text-white mb-2">{feat.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feat.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>

      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full max-w-7xl mx-auto px-6 py-8 border-t border-slate-800/80 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-slate-500">
        <div>&copy; {new Date().getFullYear()} LearnHub Aggregator. Built with React & FastAPI.</div>
        <div className="flex gap-6">
          <a href="#" className="hover:text-slate-300 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-slate-300 transition-colors">Terms of Service</a>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="hover:text-slate-300 transition-colors">GitHub</a>
        </div>
      </footer>

    </div>
  );
}
