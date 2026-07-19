import { useState } from 'react';
import type { FormEvent } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { motion } from 'framer-motion';
import { User, Settings, Save } from 'lucide-react';

const PRESET_AVATARS = [
  'https://api.dicebear.com/7.x/bottts/svg?seed=Felix',
  'https://api.dicebear.com/7.x/bottts/svg?seed=Aneka',
  'https://api.dicebear.com/7.x/bottts/svg?seed=Jack',
  'https://api.dicebear.com/7.x/bottts/svg?seed=Milo',
  'https://api.dicebear.com/7.x/bottts/svg?seed=Toby',
  'https://api.dicebear.com/7.x/bottts/svg?seed=Luna'
];

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [avatar, setAvatar] = useState(user?.avatar || PRESET_AVATARS[0]);
  const [isSaving, setIsSaving] = useState(false);

  const handleUpdate = async (e: FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) return;
    setIsSaving(true);

    try {
      await updateProfile({
        full_name: fullName.trim(),
        avatar
      });
    } catch (err) {
      // toast and error already handled in context, but fallback here if needed
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      
      {/* Header */}
      <div className="flex flex-col gap-3">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-2">
          Profile Settings <Settings className="w-6 h-6 text-indigo-400" />
        </h1>
        <p className="text-slate-400 text-sm">
          Manage your account configurations, profile name, and selected digital avatar.
        </p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 md:p-8 space-y-8 relative overflow-hidden"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-[80px] pointer-events-none" />

        {/* User Card view */}
        <div className="flex items-center gap-4 border-b border-slate-800/80 pb-6">
          <div className="w-16 h-16 rounded-2xl overflow-hidden bg-slate-800 border border-slate-700/80 shrink-0">
            <img src={avatar} alt="Current avatar" className="w-full h-full object-cover" />
          </div>
          <div>
            <h3 className="text-xl font-extrabold text-white">{user?.full_name}</h3>
            <p className="text-xs text-slate-500">{user?.email} &bull; Student Account</p>
          </div>
        </div>

        {/* Edit Form */}
        <form onSubmit={handleUpdate} className="space-y-6">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Full Name
            </label>
            <div className="relative">
              <User className="w-5 h-5 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full pl-11 pr-4 py-3 bg-slate-950/50 border border-slate-700/60 rounded-xl text-slate-100 placeholder-slate-500 focus-glow"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Change Avatar
            </label>
            <div className="grid grid-cols-6 gap-3">
              {PRESET_AVATARS.map((url) => (
                <button
                  type="button"
                  key={url}
                  onClick={() => setAvatar(url)}
                  className={`w-11 h-11 rounded-xl overflow-hidden border-2 bg-slate-800 transition-all ${
                    avatar === url 
                      ? 'border-indigo-500 scale-110 shadow-lg' 
                      : 'border-transparent hover:border-slate-650'
                  }`}
                >
                  <img src={url} alt="Avatar presets" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isSaving}
            className="w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-indigo-800 disabled:to-purple-800 text-white font-medium rounded-xl transition-all shadow-lg flex items-center justify-center gap-2"
          >
            {isSaving ? (
              'Updating...'
            ) : (
              <>
                <Save className="w-4 h-4" /> Save Settings
              </>
            )}
          </button>
        </form>

      </motion.div>

    </div>
  );
}

