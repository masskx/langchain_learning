import { useState, useRef, useCallback, useEffect } from 'react'
import { streamChat, fetchMessages, clearMessages, uploadImage } from '../api/chat'

// 生成简单的 threadId
function newThreadId() {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

// 从 localStorage 恢复 threadId
function getStoredThreadId() {
  try {
    const stored = localStorage.getItem('chef_thread_id')
    if (stored) return stored
  } catch { /* ignore */ }
  return newThreadId()
}

/**
 * useChat — 管理对话状态、流式响应、图片上传
 *
 * 返回:
 *   messages      当前消息列表
 *   isStreaming   是否正在流式输出
 *   threadId      当前会话 ID
 *   sendMessage   发送消息
 *   newSession    新建会话
 *   uploadFile    上传图片
 *   uploading     是否正在上传
 */
export function useChat() {
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [threadId, setThreadId] = useState(getStoredThreadId)
  const abortRef = useRef(false)

  // 启动时加载历史消息
  useEffect(() => {
    let cancelled = false
    fetchMessages(threadId)
      .then(msgs => {
        if (!cancelled) setMessages(msgs)
      })
      .catch(() => { /* 新会话无历史，忽略 */ })
    return () => { cancelled = true }
  }, [threadId])

  // 持久化 threadId
  useEffect(() => {
    try { localStorage.setItem('chef_thread_id', threadId) } catch { /* ignore */ }
  }, [threadId])

  /** 发送消息 */
  const sendMessage = useCallback(async (text, imageUrl) => {
    const userMsg = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: text,
      imageUrl: imageUrl || null,
    }

    // 给助手消息占位
    const assistantId = `msg_${Date.now() + 1}`
    const assistantMsg = {
      id: assistantId,
      role: 'assistant',
      content: '',
      streaming: true,
    }

    setMessages(prev => [...prev, userMsg, assistantMsg])
    setIsStreaming(true)
    abortRef.current = false

    await streamChat(
      { message: text, imageUrl, threadId },
      // onToken: 逐块追加到助手消息
      (token) => {
        if (abortRef.current) return
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? { ...m, content: m.content + token }
              : m
          )
        )
      },
      // onDone: 标记流式完成
      () => {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId ? { ...m, streaming: false } : m
          )
        )
        setIsStreaming(false)
      },
      // onError
      (err) => {
        console.error('对话失败:', err)
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? { ...m, content: '抱歉，出了点问题，请稍后再试 🙇', streaming: false }
              : m
          )
        )
        setIsStreaming(false)
      }
    )
  }, [threadId])

  /** 新建会话 */
  const newSession = useCallback(async () => {
    try { await clearMessages(threadId) } catch { /* ignore */ }
    const id = newThreadId()
    setThreadId(id)
    setMessages([])
    setIsStreaming(false)
  }, [threadId])

  /** 上传图片到 OSS，返回 accessUrl */
  const uploadFile = useCallback(async (file) => {
    setUploading(true)
    try {
      return await uploadImage(file)
    } finally {
      setUploading(false)
    }
  }, [])

  return {
    messages,
    isStreaming,
    uploading,
    threadId,
    sendMessage,
    newSession,
    uploadFile,
  }
}
