import { useState } from 'react'
import { Sparkles, User, ImageIcon, Copy, Check, ThumbsUp, ThumbsDown } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

/**
 * AI 消息的 Markdown 自定义渲染组件
 */
function MarkdownContent({ children }) {
  return (
    <ReactMarkdown
      components={{
        h1: ({ children }) => <h1 className="text-lg font-bold text-stone-800 mt-3 mb-1.5 first:mt-0">{children}</h1>,
        h2: ({ children }) => <h2 className="text-base font-bold text-stone-800 mt-2.5 mb-1 first:mt-0">{children}</h2>,
        h3: ({ children }) => <h3 className="text-sm font-semibold text-stone-700 mt-2 mb-0.5 first:mt-0">{children}</h3>,
        p: ({ children }) => <p className="mb-1.5 last:mb-0">{children}</p>,
        ul: ({ children }) => <ul className="list-disc pl-4 mb-1.5 space-y-0.5 last:mb-0">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-4 mb-1.5 space-y-0.5 last:mb-0">{children}</ol>,
        li: ({ children }) => <li className="text-stone-700">{children}</li>,
        code: ({ className, children, ...props }) => {
          const isBlock = className?.startsWith('language-')
          if (isBlock) {
            return <code className="block bg-stone-800 text-emerald-300 text-xs px-3 py-2 rounded-lg my-1.5 overflow-x-auto">{children}</code>
          }
          return <code className="bg-amber-100 text-amber-800 text-xs px-1.5 py-0.5 rounded font-mono" {...props}>{children}</code>
        },
        strong: ({ children }) => <strong className="font-semibold text-stone-800">{children}</strong>,
        em: ({ children }) => <em className="italic text-stone-600">{children}</em>,
        hr: () => <hr className="my-2 border-stone-200" />,
        blockquote: ({ children }) => (
          <blockquote className="border-l-3 border-amber-400 pl-3 my-1.5 text-stone-600 italic">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-1.5">
            <table className="w-full text-xs border-collapse">{children}</table>
          </div>
        ),
        th: ({ children }) => <th className="border border-stone-300 bg-stone-100 px-2 py-1 text-left font-semibold">{children}</th>,
        td: ({ children }) => <td className="border border-stone-300 px-2 py-1">{children}</td>,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-amber-600 underline hover:text-amber-800">
            {children}
          </a>
        ),
      }}
    >
      {children}
    </ReactMarkdown>
  )
}

/**
 * 消息气泡
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const isStreaming = message.streaming
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState(null) // null | 'up' | 'down'

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // fallback
      const ta = document.createElement('textarea')
      ta.value = message.content
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleFeedback = (type) => {
    setFeedback(prev => prev === type ? null : type)
    // TODO: 后续接入后端反馈 API
  }

  return (
    <div className={`flex gap-3 animate-slide-up group ${isUser ? 'flex-row-reverse' : ''}`}>
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
          <div className={`relative
            px-4 py-2.5 rounded-2xl text-sm leading-relaxed break-words
            ${isUser
              ? 'bg-gradient-to-br from-amber-50 to-orange-100 text-stone-700 border border-amber-200/50 whitespace-pre-wrap'
              : 'bg-white/80 backdrop-blur-sm text-stone-700 border border-stone-200/50 shadow-sm'
            }
          `}>
            {isUser ? message.content : <MarkdownContent>{message.content}</MarkdownContent>}

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

        {/* AI 消息的操作按钮栏 */}
        {!isUser && !isStreaming && message.content && (
          <div className="flex items-center gap-1 mt-1 px-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {/* 复制 */}
            <button
              onClick={handleCopy}
              className="p-1.5 rounded-lg text-stone-400 hover:text-stone-600 hover:bg-stone-100/80 transition-colors"
              title="复制内容"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>

            {/* 分隔 */}
            <span className="w-px h-3 bg-stone-200" />

            {/* 点赞 */}
            <button
              onClick={() => handleFeedback('up')}
              className={`p-1.5 rounded-lg transition-colors
                ${feedback === 'up'
                  ? 'text-amber-500 bg-amber-50'
                  : 'text-stone-400 hover:text-amber-500 hover:bg-amber-50/50'
                }`}
              title="有帮助"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>

            {/* 点踩 */}
            <button
              onClick={() => handleFeedback('down')}
              className={`p-1.5 rounded-lg transition-colors
                ${feedback === 'down'
                  ? 'text-rose-500 bg-rose-50'
                  : 'text-stone-400 hover:text-rose-500 hover:bg-rose-50/50'
                }`}
              title="不够好"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
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
