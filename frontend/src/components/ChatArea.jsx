import { useRef, useEffect } from 'react'
import { UtensilsCrossed, ChefHat } from 'lucide-react'
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
    <div className="flex-1 overflow-y-auto px-4 pb-4 pt-20 scrollbar-thin">
      <div className="max-w-3xl mx-auto">
        {isEmpty ? (
          /* 空状态 */
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            {/* 装饰图标 */}
            <div className="relative mb-8">
              <div className="absolute inset-0 bg-amber-200 rounded-full blur-2xl opacity-40 animate-pulse-soft" />
              <div className="relative p-5 bg-white/80 backdrop-blur-sm rounded-3xl shadow-lg border border-white/60">
                <ChefHat className="w-16 h-16 text-amber-500" strokeWidth={1.5} />
              </div>
            </div>

            <h2 className="text-xl sm:text-2xl font-semibold text-stone-700 mb-2">
              今天想吃点什么？
            </h2>
            <p className="text-stone-400 max-w-xs leading-relaxed text-sm sm:text-base">
              上传食材照片或直接描述你手头的食材，
              <br />
              AI 私厨会帮你找到最佳食谱搭配 🍳
            </p>

            {/* 提示卡片 */}
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-lg">
              {[
                { icon: '🥬', text: '拍一张冰箱里的食材' },
                { icon: '🍳', text: 'AI 分析并检索菜谱' },
                { icon: '📋', text: '获取结构化食谱推荐' },
              ].map(({ icon, text }) => (
                <div
                  key={text}
                  className="flex flex-col items-center gap-2 p-4 rounded-2xl
                             bg-white/60 backdrop-blur-sm border border-stone-100
                             hover:bg-white/90 hover:shadow-sm transition-all duration-200"
                >
                  <span className="text-3xl">{icon}</span>
                  <span className="text-xs text-stone-500">{text}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          /* 消息列表 */
          <div className="flex flex-col gap-4 pb-2">
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
