import { useState } from 'react'
import {
  ChefHat, MessageCircle, BookOpen, CalendarDays, Package,
  Settings, Cpu, Sparkles, ChevronLeft, User, Star,
  Clock, Flame, Heart
} from 'lucide-react'

/**
 * 侧边栏 —— 用户信息、导航、模型选择、功能占位
 * isOpen / onClose 控制开关合
 */
export default function Sidebar({ isOpen, onClose, user }) {
  const [activeModel, setActiveModel] = useState('qwen')

  const navItems = [
    { id: 'chat', label: '智能对话', icon: MessageCircle, active: true },
    { id: 'recipes', label: '食谱库', icon: BookOpen, active: false, soon: true },
    { id: 'mealplan', label: '周食谱计划', icon: CalendarDays, active: false, soon: true },
    { id: 'inventory', label: '食材库存', icon: Package, active: false, soon: true },
    { id: 'settings', label: '偏好设置', icon: Settings, active: false, soon: true },
  ]

  const models = [
    { id: 'qwen', label: 'Qwen 3.6', desc: '推荐 · 综合能力强', color: 'from-blue-500 to-cyan-500' },
    { id: 'deepseek', label: 'DeepSeek V4', desc: '逻辑推理强', color: 'from-emerald-500 to-teal-500' },
  ]

  return (
    <>
      {/* 移动端遮罩 */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* 侧边栏本体 */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-72
        bg-white/85 backdrop-blur-2xl border-r border-stone-200/50
        shadow-xl shadow-stone-200/20
        flex flex-col
        transform transition-transform duration-300 ease-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
      `}>
        {/* 顶部 Logo 区 */}
        <div className="p-5 border-b border-stone-100/80">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-gradient-to-br from-amber-400 via-orange-500 to-rose-500 rounded-xl shadow-md">
                <ChefHat className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  AI 私厨
                </h2>
                <p className="text-xs text-stone-400">DevChef</p>
              </div>
            </div>
            {/* 关闭按钮（移动端） */}
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-stone-400 hover:text-stone-600 hover:bg-stone-100 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 用户信息卡片 */}
        <div className="px-4 pt-4 pb-3">
          <div className="flex items-center gap-3 p-3 rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-100/50">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-sm">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-stone-700 truncate">{user}</p>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-amber-200/50 text-xs text-amber-700">
                  <Flame className="w-3 h-3" /> 程序员
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 模型选择器 */}
        <div className="px-4 py-2">
          <p className="text-xs font-medium text-stone-400 uppercase tracking-wider mb-2 px-2">
            模型选择
          </p>
          <div className="space-y-1.5">
            {models.map(m => (
              <button
                key={m.id}
                onClick={() => setActiveModel(m.id)}
                className={`w-full text-left p-2.5 rounded-xl transition-all duration-200
                  ${activeModel === m.id
                    ? 'bg-white shadow-sm border border-amber-200/60 ring-1 ring-amber-100'
                    : 'hover:bg-white/60 border border-transparent'
                  }`}
              >
                <div className="flex items-center gap-2.5">
                  <div className={`w-2.5 h-2.5 rounded-full bg-gradient-to-r ${m.color}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-stone-700">{m.label}</p>
                    <p className="text-xs text-stone-400">{m.desc}</p>
                  </div>
                  {activeModel === m.id && (
                    <div className="w-2 h-2 rounded-full bg-amber-500" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 导航菜单 */}
        <nav className="px-4 py-3 flex-1">
          <p className="text-xs font-medium text-stone-400 uppercase tracking-wider mb-2 px-2">
            功能导航
          </p>
          <ul className="space-y-1">
            {navItems.map(item => (
              <li key={item.id}>
                <button
                  disabled={item.soon}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                    transition-all duration-200 group
                    ${item.active
                      ? 'bg-gradient-to-r from-amber-100/80 to-orange-100/80 text-amber-800 border border-amber-200/50'
                      : 'text-stone-500 hover:text-stone-700 hover:bg-white/60 border border-transparent'
                    }
                    ${item.soon ? 'cursor-not-allowed opacity-60' : ''}
                  `}
                >
                  <item.icon className={`w-4.5 h-4.5 ${item.active ? 'text-amber-600' : 'text-stone-400 group-hover:text-stone-500'}`} />
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.soon && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-stone-100 text-stone-400 font-normal">
                      即将上线
                    </span>
                  )}
                  {item.active && !item.soon && (
                    <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                  )}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* 底部信息 */}
        <div className="px-4 pb-4 pt-2 border-t border-stone-100/80">
          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-1.5 text-xs text-stone-400">
              <Sparkles className="w-3.5 h-3.5" />
              <span>DevChef v0.1</span>
            </div>
            <div className="flex items-center gap-1">
              <Heart className="w-3.5 h-3.5 text-rose-400 fill-rose-400" />
              <Clock className="w-3.5 h-3.5 text-stone-300" />
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
