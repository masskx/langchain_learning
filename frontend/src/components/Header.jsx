import { ChefHat, Plus } from 'lucide-react'

export default function Header({ onNewSession, disabled }) {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 p-3 sm:p-4">
      <div className="max-w-3xl mx-auto bg-white/70 backdrop-blur-xl rounded-2xl shadow-sm border border-white/60 px-4 sm:px-6 py-3 flex items-center justify-between">
        {/* Logo + 标题 */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-amber-400 via-orange-500 to-rose-500 rounded-xl shadow-md">
            <ChefHat className="w-5 h-5 sm:w-6 sm:h-6 text-white" strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
              AI 私厨
            </h1>
            <p className="text-xs text-stone-400 hidden sm:block">
              上传食材，获取专属食谱
            </p>
          </div>
        </div>

        {/* 新建会话 */}
        <button
          onClick={onNewSession}
          disabled={disabled}
          className="flex items-center gap-1.5 px-3 sm:px-4 py-2 text-sm font-medium
                     bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600
                     text-white rounded-xl transition-all duration-200 shadow-sm hover:shadow-md
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">新建会话</span>
        </button>
      </div>
    </header>
  )
}
