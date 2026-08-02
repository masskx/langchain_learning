// API 基础地址：开发时 Vite proxy 代理到 FastAPI，生产环境同源部署
const BASE = '/api/v1'

/**
 * 流式对话 —— POST /api/v1/chat/stream
 * 返回 ReadableStream reader，调用者逐块读取
 */
export async function streamChat({ message, imageUrl, threadId }, onToken, onDone, onError) {
  try {
    const res = await fetch(`${BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        image_url: imageUrl || null,
        thread_id: threadId,
      }),
    })

    if (!res.ok) throw new Error(`请求失败 (${res.status})`)

    const reader = res.body?.getReader()
    if (!reader) throw new Error('浏览器不支持流式读取')

    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        onDone?.()
        break
      }
      onToken(decoder.decode(value, { stream: true }))
    }
  } catch (err) {
    onError?.(err)
  }
}

/**
 * 获取历史消息 —— GET /api/v1/chat/messages
 */
export async function fetchMessages(threadId) {
  const res = await fetch(`${BASE}/chat/messages?thread_id=${threadId}`)
  if (!res.ok) throw new Error(`获取历史消息失败 (${res.status})`)
  const data = await res.json()
  return data.messages || []
}

/**
 * 清空会话 —— DELETE /api/v1/chat/messages
 */
export async function clearMessages(threadId) {
  const res = await fetch(`${BASE}/chat/messages?thread_id=${threadId}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error(`清空会话失败 (${res.status})`)
}

/**
 * 获取 OSS 上传预签名 URL —— GET /api/v1/oss/presign
 */
export async function getPresignedUrl(filename) {
  const res = await fetch(`${BASE}/oss/presign?filename=${encodeURIComponent(filename)}`)
  if (!res.ok) throw new Error(`获取上传凭证失败 (${res.status})`)
  return res.json()
}

/**
 * 上传图片到 OSS
 */
export async function uploadImage(file) {
  const { uploadUrl, accessUrl, contentType } = await getPresignedUrl(file.name)

  const res = await fetch(uploadUrl, {
    method: 'PUT',
    body: file,
    headers: { 'Content-Type': contentType },
  })

  if (!res.ok) throw new Error(`图片上传失败 (${res.status})`)
  return accessUrl
}
