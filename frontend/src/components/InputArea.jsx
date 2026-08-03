import { useState, useRef, useCallback } from 'react'
import { Send, ImagePlus, X, Loader2, Lightbulb } from 'lucide-react'

/** 快捷提示词 */
const SUGGESTIONS = [
  { icon: '🥬', text: '冰箱里有啥做啥' },
  { icon: '🍅', text: '西红柿和鸡蛋怎么做？' },
  { icon: '🥩', text: '推荐低脂高蛋白菜谱' },
  { icon: '⏱️', text: '15分钟快手晚餐' },
]

/**
 * 输入区域 — 图片上传 + 快捷提示 + 文字输入 + 发送
 */
export default function InputArea({ onSend, onUpload, isStreaming, uploading }) {
  const [text, setText] = useState('')
  const [preview, setPreview] = useState(null)   // { file, url }
  const fileInputRef = useRef(null)
  const textareaRef = useRef(null)

  // 自动调整 textarea 高度
  const adjustHeight = useCallback(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 120) + 'px'
  }, [])

  const handleSend = async () => {
    const trimmed = text.trim()
    if (!trimmed && !preview) return
    if (isStreaming) return

    let imageUrl = null
    if (preview?.file) {
      imageUrl = await onUpload(preview.file)
    }

    setText('')
    setPreview(null)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    onSend(trimmed || '这是我冰箱里的食物，帮我看看能做什么佳肴？', imageUrl)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setPreview({ file, url: URL.createObjectURL(file) })
    if (!text.trim()) {
      setText('这是我冰箱里的食材，帮我推荐食谱~')
    }
  }

  const clearPreview = () => {
    if (preview?.url) URL.revokeObjectURL(preview.url)
    setPreview(null)
  }

  const canSend = (text.trim() || preview) && !isStreaming && !uploading

  return (
    <div className="sticky bottom-0 z-30 p-3 sm:p-4">
      <div className="max-w-3xl mx-auto">

        {/* 快捷提示芯片 */}
        <div className="flex items-center gap-2 mb-2.5 px-1 overflow-x-auto scrollbar-thin pb-1">
          <Lightbulb className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
          {SUGGESTIONS.map(({ icon, text: label }) => (
            <button
              key={label}
              onClick={() => {
                setText(label)
                textareaRef.current?.focus()
              }}
              disabled={isStreaming}
              className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full
                         bg-white/60 backdrop-blur-sm border border-stone-200/50
                         text-xs text-stone-500 hover:text-stone-700 hover:bg-white hover:border-amber-200
                         hover:shadow-sm transition-all duration-200
                         disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span className="text-sm">{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* 输入卡片 */}
        <div className="bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg border border-white/60">

          {/* 图片预览 */}
          {preview && (
            <div className="px-4 pt-3 animate-fade-in">
              <div className="relative inline-block">
                <img
                  src={preview.url}
                  alt="预览"
                  className="w-20 h-20 rounded-xl object-cover border-2 border-amber-200 shadow-sm"
                />
                <button
                  onClick={clearPreview}
                  className="absolute -top-2 -right-2 p-1 bg-white rounded-full shadow-md
                             text-stone-400 hover:text-rose-500 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
                {uploading && (
                  <div className="absolute inset-0 bg-black/30 rounded-xl flex items-center justify-center">
                    <Loader2 className="w-5 h-5 text-white animate-spin" />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 输入栏 */}
          <div className="flex items-end gap-2 p-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isStreaming}
              className="flex-shrink-0 p-2.5 text-stone-400 hover:text-amber-500 hover:bg-amber-50
                         rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="上传食材图片"
            >
              <ImagePlus className="w-5 h-5" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />

            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => { setText(e.target.value); adjustHeight() }}
              onKeyDown={handleKeyDown}
              placeholder="描述你的食材或直接问菜谱..."
              rows={1}
              disabled={isStreaming}
              className="flex-1 bg-stone-50/80 border-0 rounded-2xl px-4 py-2.5 resize-none text-sm
                         placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-amber-300
                         focus:bg-white transition-all disabled:opacity-50"
            />

            <button
              onClick={handleSend}
              disabled={!canSend}
              className="flex-shrink-0 p-2.5 rounded-xl transition-all duration-200 shadow-sm
                         bg-gradient-to-r from-amber-500 to-orange-500
                         hover:from-amber-600 hover:to-orange-600 hover:shadow-md
                         disabled:from-stone-200 disabled:to-stone-200 disabled:shadow-none
                         disabled:cursor-not-allowed text-white"
            >
              {isStreaming || uploading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
