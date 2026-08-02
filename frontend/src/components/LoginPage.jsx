import { useState } from 'react'
import { ChefHat, Lock, User, LogIn } from 'lucide-react'

const DEFAULT_USERNAME = 'admin'
const DEFAULT_PASSWORD = 'admin'

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // 模拟网络延迟，让体验更真实
    setTimeout(() => {
      if (username === DEFAULT_USERNAME && password === DEFAULT_PASSWORD) {
        onLogin(username)
      } else {
        setError('账号或密码错误，请重试')
      }
      setLoading(false)
    }, 600)
  }

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4">
      {/* 背景层 —— 和主应用保持一致 */}
      <div className="fixed inset-0 bg-gradient-to-br from-amber-50 via-orange-50/50 to-rose-50/30" />
      <div className="fixed inset-0 opacity-40 pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-amber-200 rounded-full mix-blend-multiply blur-3xl animate-pulse-soft" />
        <div className="absolute top-40 right-10 w-96 h-96 bg-orange-200 rounded-full mix-blend-multiply blur-3xl animate-pulse-soft" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-rose-200 rounded-full mix-blend-multiply blur-3xl animate-pulse-soft" style={{ animationDelay: '2s' }} />
      </div>

      {/* 登录卡片 */}
      <div className="relative w-full max-w-md animate-fade-in">
        {/* 毛玻璃卡片 */}
        <div className="bg-white/70 backdrop-blur-xl rounded-3xl shadow-xl border border-white/60 p-8 sm:p-10">
          {/* Logo 区 */}
          <div className="text-center mb-8">
            <div className="inline-flex p-4 bg-gradient-to-br from-amber-400 via-orange-500 to-rose-500 rounded-2xl shadow-lg mb-5">
              <ChefHat className="w-10 h-10 text-white" strokeWidth={2} />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
              AI 私厨
            </h1>
            <p className="mt-2 text-sm text-stone-400">
              上传食材，获取专属食谱推荐
            </p>
          </div>

          {/* 登录表单 */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* 用户名 */}
            <div className="relative">
              <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" strokeWidth={1.5} />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="请输入账号"
                className="w-full pl-11 pr-4 py-3.5 bg-white/60 border border-stone-200/60 rounded-xl
                           text-sm text-stone-700 placeholder:text-stone-400
                           focus:outline-none focus:border-amber-400 focus:ring-4 focus:ring-amber-100/50
                           transition-all duration-200"
                autoComplete="username"
              />
            </div>

            {/* 密码 */}
            <div className="relative">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" strokeWidth={1.5} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="请输入密码"
                className="w-full pl-11 pr-4 py-3.5 bg-white/60 border border-stone-200/60 rounded-xl
                           text-sm text-stone-700 placeholder:text-stone-400
                           focus:outline-none focus:border-amber-400 focus:ring-4 focus:ring-amber-100/50
                           transition-all duration-200"
                autoComplete="current-password"
              />
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="text-sm text-red-500 bg-red-50/80 rounded-xl px-4 py-3 text-center animate-fade-in">
                {error}
              </div>
            )}

            {/* 登录按钮 */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-6 py-3.5
                         bg-gradient-to-r from-amber-500 to-orange-500
                         hover:from-amber-600 hover:to-orange-600
                         text-white font-semibold rounded-xl
                         transition-all duration-200 shadow-md hover:shadow-lg
                         disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <LogIn className="w-5 h-5" />
              {loading ? '验证中...' : '登 录'}
            </button>
          </form>

          {/* 底部提示 */}
          <p className="mt-6 text-center text-xs text-stone-400">
            默认账号：admin / admin
          </p>
        </div>
      </div>
    </div>
  )
}