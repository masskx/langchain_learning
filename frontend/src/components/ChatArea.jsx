import { useRef, useEffect } from 'react'
import { ChefHat, Camera, Search, ClipboardList, Sparkles } from 'lucide-react'
import MessageBubble from './MessageBubble'

/**
 * 聊天区域 — 消息列表 + 空状态引导
 */
export default function ChatArea({ messages, isStreaming }) {
  const bottomRef = useRef(null)

  // 自动滚到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const isEmpty = messages.length === 0

  return (
    <div className="flex-1 overflow-y-auto px-4 pb-4 pt-2 scrollbar-thin">
      <div className="max-w-3xl mx-auto">
        {isEmpty ? (
          /* ====== 空状态 ====== */
          <div className="flex flex-col items-center justify-center min-h-[65vh] text-center px-4">
            {/* 大 Logo */}
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-amber-200 rounded-full blur-3xl opacity-50 animate-pulse-soft" />
              <div className="relative p-6 bg-white/70 backdrop-blur-sm rounded-3xl shadow-lg border border-white/60">
                <ChefHat className="w-20 h-20 text-amber-500" strokeWidth={1} />
              </div>
            </div>

            <h2 className="text-2xl sm:text-3xl font-bold text-stone-700 mb-3">
              今天想吃点什么？
            </h2>
            <p className="text-stone-400 max-w-md leading-relaxed text-sm sm:text-base mb-10">
              拍一张冰箱照片，或者告诉我你手头有什么食材，
              <br />
              AI 私厨帮你找到最合适的食谱搭配 🍳
            </p>

            {/* 三步骤引导卡片 */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-2xl">
              {[
                {
                  icon: Camera,
                  title: '拍食材',
                  desc: '拍下冰箱里的食材照片上传',
                  color: 'from-amber-400 to-orange-500',
                  bg: 'bg-amber-50',
                },
                {
                  icon: Search,
                  title: 'AI 检索',
                  desc: '本地食谱库 + 联网搜索双重匹配',
                  color: 'from-emerald-400 to-teal-500',
                  bg: 'bg-emerald-50',
                },
                {
                  icon: ClipboardList,
                  title: '获推荐',
                  desc: '结构化食谱报告，营养评分一目了然',
                  color: 'from-rose-400 to-pink-500',
                  bg: 'bg-rose-50',
                },
              ].map(({ icon: Icon, title, desc, color, bg }, i) => (
                <div
                  key={title}
                  className={`group flex flex-col items-center gap-3 p-5 rounded-2xl
                    ${bg}/60 backdrop-blur-sm border border-white/60
                    hover:shadow-md hover:scale-[1.02] transition-all duration-300`}
                >
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${color} shadow-sm
                    group-hover:shadow-md transition-shadow duration-300`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-stone-700 mb-0.5">{title}</p>
                    <p className="text-xs text-stone-400 leading-relaxed">{desc}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* 底部装饰 */}
            <div className="mt-10 flex items-center gap-2 text-xs text-stone-300">
              <Sparkles className="w-3.5 h-3.5" />
              <span>本地食谱库 383 道 + 互联网实时搜索</span>
            </div>
          </div>
        ) : (
          /* ====== 消息列表 ====== */
          <div className="flex flex-col gap-4 pb-4">
            {messages.map(msg => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* 滚动锚点 */}
            <div ref={bottomRef} />
          </div>
        )}
      </div>
    </div>
  )
}
