import { Sparkles, Bot, User, ImageIcon } from 'lucide-react'

/**
 * 消息气泡
 * - user: 右对齐，暖色背景
 * - assistant: 左对齐，白色背景 + 流式光标
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const isStreaming = message.streaming

  return (
    <div className={`flex gap-3 animate-slide-up ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* 头像 */}
      <div className={`
        flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center shadow-sm
        ${isUser
          ? 'bg-gradient-to-br from-amber-400 to-orange-500'
          : 'bg-gradient-to-br from-emerald-400 to-teal-500'
        }
      `}>
        {isUser
          ? <User className="w-4 h-4 text-white" />
          : <Sparkles className="w-4 h-4 text-white" />
        }
      </div>

      {/* 气泡内容 */}
      <div className={`max-w-[80%] min-w-0 ${isUser ? 'items-end' : 'items-start'}`}>
        {/* 文字内容 */}
        {message.content && (
          <div className={`
            px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap break-words
            ${isUser
              ? 'bg-gradient-to-br from-amber-50 to-orange-100 text-stone-700 border border-amber-200/50'
              : 'bg-white/80 backdrop-blur-sm text-stone-700 border border-stone-200/50 shadow-sm'
            }
          `}>
            {message.content}
            {/* 流式光标 */}
            {isStreaming && (
              <span className="inline-flex ml-0.5">
                <span className="w-1.5 h-4 bg-amber-500 rounded-full animate-pulse-soft" />
              </span>
            )}
          </div>
        )}

        {/* 流式等待（还没有内容时） */}
        {isStreaming && !message.content && (
          <div className="px-4 py-3 rounded-2xl bg-white/80 border border-stone-200/50 shadow-sm">
            <span className="flex gap-1.5">
              <span className="w-2 h-2 bg-amber-400 rounded-full animate-dot-pulse" style={{ animationDelay: '0s' }} />
              <span className="w-2 h-2 bg-amber-400 rounded-full animate-dot-pulse" style={{ animationDelay: '0.2s' }} />
              <span className="w-2 h-2 bg-amber-400 rounded-full animate-dot-pulse" style={{ animationDelay: '0.4s' }} />
            </span>
          </div>
        )}

        {/* 图片预览 */}
        {message.imageUrl && (
          <div className={`mt-1.5 ${isUser ? 'flex justify-end' : ''}`}>
            <div className="relative group">
              <img
                src={message.imageUrl}
                alt="食材图片"
                className="max-w-48 max-h-48 rounded-xl object-cover border-2 border-white shadow-md
                           transition-transform duration-200 group-hover:scale-105"
              />
              <div className="absolute bottom-1.5 left-1.5 flex items-center gap-1 px-2 py-0.5
                              bg-black/40 backdrop-blur-sm rounded-lg text-white text-xs">
                <ImageIcon className="w-3 h-3" />
                食材
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
