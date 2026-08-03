import { ChefHat, Plus, LogOut, Menu } from 'lucide-react'

export default function Header({ onNewSession, disabled, user, onLogout, onToggleSidebar }) {
  return (
    <header className="sticky top-0 z-30 p-3 sm:p-4">
      <div className="bg-white/70 backdrop-blur-xl rounded-2xl shadow-sm border border-white/60 px-4 sm:px-5 py-3 flex items-center justify-between">
        {/* 左侧：菜单按钮 + Logo */}
        <div className="flex items-center gap-3">
          {/* 侧边栏切换按钮 */}
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-xl text-stone-400 hover:text-stone-600 hover:bg-stone-100/80 transition-all duration-200 lg:hidden"
            title="菜单"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2.5">
            <div className="p-1.5 bg-gradient-to-br from-amber-400 via-orange-500 to-rose-500 rounded-lg shadow-sm">
              <ChefHat className="w-4 h-4 text-white" strokeWidth={2} />
            </div>
            <h1 className="text-base sm:text-lg font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
              智能对话
            </h1>
          </div>
        </div>

        {/* 右侧操作区 */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          {/* 退出登录 */}
          {onLogout && (
            <button
              onClick={onLogout}
              className="flex items-center gap-1 px-2.5 py-2 text-xs sm:text-sm font-medium
                         text-stone-400 hover:text-stone-600 hover:bg-stone-100/80
                         rounded-xl transition-all duration-200"
              title="退出登录"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">退出</span>
            </button>
          )}

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
            <span className="hidden sm:inline">新对话</span>
          </button>
        </div>
      </div>
    </header>
  )
}
